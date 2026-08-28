import io
import logging
from sqlalchemy import select
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.config import config
from bot.database.models import User
from bot.states import GenerateState
from bot.database.db_setup import async_session
from bot.services.s3 import upload_photo_to_minio
from bot.keyboards.inline import get_styles_keyboard
from bot.services.ai_api import create_nano_banana_task, wait_for_completion

router = Router()

STYLES_PROMPTS = {
    "style_cyberpunk": "Make it cyberpunk style, highly detailed, 4k resolution, neon lights, masterpiece",
    "style_anime": "Anime style, studio ghibli, masterpiece, vibrant colors, detailed illustration",
    "style_realistic": "Ultra realistic photography, 8k resolution, cinematic lighting, photorealistic"
}


@router.message(F.photo)
async def handle_photo(message: Message, state: FSMContext):
    async with async_session() as session:
        user = await session.scalar(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        
        if not user or user.balance <= 0: 
            await message.answer("❌ У вас закончились генерации! Пополните баланс.")
            return

    photo_id = message.photo[-1].file_id
    await state.update_data(photo_file_id=photo_id)

    await message.answer(
        "📸 Отличное фото! Выбери стиль для обработки или напиши свой промпт:",
        reply_markup=get_styles_keyboard()
    )
    await state.set_state(GenerateState.waiting_for_style)


@router.callback_query(F.data.startswith("style_"), GenerateState.waiting_for_style)
async def process_style_selection(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    
    style_data = callback.data
    
    if style_data == "style_custom":
        await callback.message.edit_text("✏️ Напиши на английском, что ты хочешь увидеть на фото:")
        await state.set_state(GenerateState.waiting_for_prompt)
        return

    prompt = STYLES_PROMPTS[style_data]
    await start_generation(callback.message, bot, state, prompt, callback.from_user.id)


@router.message(GenerateState.waiting_for_prompt, F.text)
async def process_custom_prompt(message: Message, state: FSMContext, bot: Bot):
    prompt = message.text
    await start_generation(message, bot, state, prompt, message.from_user.id)


async def start_generation(message: Message, bot: Bot, state: FSMContext, prompt: str, user_id: int):
    data = await state.get_data()
    photo_file_id = data.get("photo_file_id")
    
    await state.clear()
    
    if not photo_file_id:
        await message.answer("❌ Ошибка: photo_id не найден. Отправьте фото заново.")
        return

    status_msg = await message.answer("⏳ Проверяем баланс и подготавливаем запрос...")

    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == user_id))
        
        if not user or user.balance <= 0:
            await status_msg.edit_text("❌ У вас закончились генерации! Пополните баланс.")
            return
            
        user.balance -= 1
        await session.commit()
        remaining_balance = user.balance

    try:
        file_info = await bot.get_file(photo_file_id)
        image_url = f"https://api.telegram.org/file/bot{config.BOT_TOKEN}/{file_info.file_path}"

        await status_msg.edit_text(
            f"🎨 Нейросеть генерирует изображение...\n<i>Запрос: {prompt}</i>", 
            parse_mode="HTML"
        )

        task_id = await create_nano_banana_task(prompt=prompt, image_url=image_url)
        result_url = await wait_for_completion(task_id)

        await message.answer_photo(
            photo=result_url,
            caption=f"✅ Готово!\n⭐️ Осталось генераций: {remaining_balance}"
        )
        
        try:
            await status_msg.delete()
        except Exception:
            pass

    except Exception as e:
        logging.error(f"Ошибка при генерации у юзера {user_id}: {e}", exc_info=True)

        async with async_session() as session:
            user = await session.scalar(select(User).where(User.telegram_id == user_id))
            if user:
                user.balance += 1
                await session.commit()

        await status_msg.edit_text(
            "❌ Произошла ошибка во время генерации изображения.\n\n"
            "Попытка возвращена на ваш баланс. Попробуйте еще раз позже."
        )