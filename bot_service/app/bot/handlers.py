from aiogram import Router, types
from aiogram.filters import Command

from app.core.jwt import decode_and_validate
from app.infra.redis import get_redis
from app.tasks.llm_tasks import llm_request

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    """Приветственное сообщение с инструкцией по использованию бота"""
    await message.answer(
        "Это бот с доступом к большой языковой модели по JWT-токену.\n"
        "Сначала отправьте токен командой: /token <JWT>\n"
        "Потом просто напишите вопрос и я с удовольствием отвечу!"
    )

@router.message(Command("token"))
async def cmd_token(message: types.Message) -> None:
    """Сохраняет JWT токен в Redis после валидации"""
    try:
        _, token = message.text.split(maxsplit=1)
    except ValueError:
        await message.answer("Использование: /token <JWT>")
        return
    try:
        decode_and_validate(token)
    except ValueError:
        await message.answer(
            "Токен невалиден. Пожалуйста, получите новый токен в Auth Service."
        )
        return
    user_id = message.from_user.id
    redis = get_redis()
    await redis.set(f"token:{user_id}", token)
    await message.answer(f"Токен для пользователя {user_id} сохранен! Теперь можно отправлять запросы модели.")

@router.message()
async def handle_text(message: types.Message) -> None:
    """Обрабатывает текстовые сообщения: проверяет токен и отправляет задачу в Celery"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    redis = get_redis()
    token = await redis.get(f"token:{user_id}")
    if not token:
        await message.answer(
            "Доступ запрещен. "
            "Сначала получите токен в Auth Service и отправьте его командой /token <JWT>"
        )
        return
    try:
        decode_and_validate(token)
    except ValueError:
        await message.answer(
            "Ваш токен истёк или невалиден. "
            "Пожалуйста, получите новый токен в Auth Service и отправьте его командой /token <JWT>"
        )
        return
    prompt = message.text or ""
    if not prompt.strip():
        await message.answer("Введите ваш запрос.")
        return
    llm_request.delay(chat_id, prompt)
    await message.answer("Запрос принят в обработку. Ответ придёт следующим сообщением.")
