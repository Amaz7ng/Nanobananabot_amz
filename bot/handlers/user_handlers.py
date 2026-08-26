from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from sqlalchemy import select

from bot.database.models import User
from bot.database.db_setup import async_session

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    async with async_session() as session:
        user = await session.scalar(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        
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
                f"Просто отправь мне фото."
            )
        else:
            await message.answer(
                f"С возвращением, {message.from_user.first_name}!\n\n"
                f"Твой баланс: {user.balance} генераций.\n"
                f"Жду фото!"
            )