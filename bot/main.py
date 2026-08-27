import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession

from bot.config import config
from bot.database.db_setup import init_db
from bot.handlers.user_handlers import router as user_router
from bot.handlers.payment_handlers import router as payment_router
from bot.handlers.generate_handlers import router as generate_router

async def main():
    logging.basicConfig(level=logging.INFO)
    
    await init_db()
    
    session = AiohttpSession(
        timeout=60,
        # proxy="http://127.0.0.1:10808" 
    )
    
    bot = Bot(token=config.BOT_TOKEN, session=session)
    
    dp = Dispatcher()
    dp.include_router(payment_router)
    dp.include_router(user_router)
    dp.include_router(generate_router)
    
    print("Start")
    
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    asyncio.run(main())