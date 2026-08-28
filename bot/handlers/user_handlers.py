from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from sqlalchemy import select

from bot.database.models import User
from bot.database.db_setup import async_session
from bot.keyboards.reply import get_main_keyboard

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    async with async_session() as session:
        user = await session.scalar(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        
        main_kb = get_main_keyboard()
        
        if not user:
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                full_name=message.from_user.full_name,
                balance=5
            )
            session.add(user)
            await session.commit()
            
            await message.answer(
                f"Привет, {message.from_user.first_name}! \n\n"
                f"Я ИИ по обработке фото. Тебе начислено {user.balance} бесплатных генераций!\n"
                f"Воспользуйся меню ниже или просто отправь мне фото.",
                reply_markup=main_kb
            )
        else:
            await message.answer(
                f"С возвращением, {message.from_user.first_name}!\n\n"
                f"Твой баланс: {user.balance} генераций.\n"
                f"Жду фото!",
                reply_markup=main_kb
            )
            
@router.message(F.text == "👤 Профиль")
async def profile_handler(message: Message):
    async with async_session() as session:
        user = await session.scalar(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        
        if user:
            await message.answer(
                f"👤 <b>Твой профиль</b>\n\n"
                f"ID: <code>{user.telegram_id}</code>\n"
                f"Имя: {user.full_name or 'Не указано'}\n"
                f"Баланс: {user.balance} ⭐️ генераций",
                parse_mode="HTML"
            )