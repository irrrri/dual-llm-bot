import asyncio

import httpx

from app.core.config import settings
from app.infra.celery_app import celery_app
from app.services.openrouter_client import call_openrouter

@celery_app.task(name="llm_request", bind=True, max_retries=2)
def llm_request(self, tg_chat_id: int, prompt: str) -> str:
    """Вызывает OpenRouter LLM и отправляет ответ пользователю в Telegram"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(_process_llm_request(tg_chat_id, prompt))
            return result
        finally:
            loop.close()
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)
    
    
async def _process_llm_request(tg_chat_id: int, prompt: str) -> str:
    """Выполняет запрос к OpenRouter API и отправляет ответ через Telegram Bot API"""
    answer = await call_openrouter(prompt)
    tg_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(tg_url, json={"chat_id": tg_chat_id, "text": answer})
        response.raise_for_status()
    return answer
