import asyncio
import logging

from app.bot.dispatcher import bot, dp

async def main() -> None:
    """Запускает polling Telegram-бота"""
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())