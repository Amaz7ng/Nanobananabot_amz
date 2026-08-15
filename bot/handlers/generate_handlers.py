import io
from aiogram import Router, F, Bot
from aiogram.types import Message
from sqlalchemy import select

from bot.database.models import User
from bot.database.db_setup import async_session
from bot.services.ai_api import create_nano_banana_task, wait_for_completion

router = Router()

@router.message(F.photo)
async def handle_photo(message: Message, bot: Bot):
    async with async_session() as session:
        user = await session.scalar(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        
        if not user or user.balance <= 0: 
            await message.answer("❌ У вас закончились попытки!")
            return

        status_msg = await message.answer("📥 Скачиваю фото и передаю в нейросеть...")

        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        photo_bytes = io.BytesIO()
        await bot.download_file(file_info.file_path, destination=photo_bytes)
        photo_bytes.seek(0)

        try:
            await status_msg.edit_text("🎨 Нейросеть генерирует изображение...")

            prompt = message.caption or "Make it cyberpunk style, detailed 4k"

            task_id = await create_nano_banana_task(prompt=prompt)

            result_url = await wait_for_completion(task_id)

            user.balance -= 1
            await session.commit()

            await message.answer_photo(
                photo=result_url,
                caption=f"✨ Готово! Осталось генераций: {user.balance}"
            )
            await status_msg.delete()

        except Exception as e:
            await status_msg.edit_text(f"❌ Произошла ошибка: {str(e)}")