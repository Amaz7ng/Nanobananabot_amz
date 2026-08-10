import asyncio
import logging

from aiogram import Bot, Dispatcher
from config import BOT_TOKEN

from handlers.user_handlers import router as user_router

async def main():
    logging.basicConfig(level=logging.INFO)
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    dp.include_router(user_router)
    
    print("Start")
    
    await dp.start_polling(bot)
    
if __name__=="__main__":
    asyncio.run(main())