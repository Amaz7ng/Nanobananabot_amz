from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
		f"Привет, {message.from_user.first_name}!\n\n"
		f"Я ии по обрабоке фото , дай фото"
	)