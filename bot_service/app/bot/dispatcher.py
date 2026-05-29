from aiogram import Bot, Dispatcher
from app.core.config import settings
from app.bot.handlers import router

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
dp.include_router(router)