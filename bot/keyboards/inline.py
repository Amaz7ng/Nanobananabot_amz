from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_styles_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🤖 Киберпанк", callback_data="style_cyberpunk")],
        [InlineKeyboardButton(text="🌸 Аниме", callback_data="style_anime")],
        [InlineKeyboardButton(text="📸 Реализм", callback_data="style_realistic")],
        [InlineKeyboardButton(text="✍️ Свой промпт", callback_data="style_custom")]
	])
    return keyboard