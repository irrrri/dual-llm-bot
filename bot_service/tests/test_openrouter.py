import pytest
import respx
from httpx import Response

from app.services.openrouter_client import call_openrouter
from app.core.config import settings


class TestOpenRouterClient:
    """Тесты клиента OpenRouter"""
    @pytest.mark.asyncio
    @respx.mock
    async def test_call_openrouter_success(self):
        """Успешный вызов OpenRouter возвращает текст ответа"""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "Это тестовый ответ от LLM"
                    }
                }
            ]
        }
        url = f"{settings.OPENROUTER_BASE_URL}/chat/completions"
        respx.post(url).mock(return_value=Response(200, json=mock_response))
        result = await call_openrouter("Какой сегодня день?")
        assert result == "Это тестовый ответ от LLM"
        assert respx.post(url).called

    @pytest.mark.asyncio
    @respx.mock
    async def test_call_openrouter_checks_request_payload(self):
        """Проверяет, что формируется правильный payload"""
        url = f"{settings.OPENROUTER_BASE_URL}/chat/completions"
        respx.post(url).mock(return_value=Response(200, json={
            "choices": [{"message": {"content": "Ответ"}}]
        }))
        prompt = "Тестовый запрос"
        await call_openrouter(prompt)
        request = respx.post(url).calls.last
        assert request is not None
        json_body = request.request.content
        import json
        body = json.loads(json_body)
        assert body["model"] == settings.OPENROUTER_MODEL
        assert body["messages"][0]["role"] == "user"
        assert body["messages"][0]["content"] == prompt

    @pytest.mark.asyncio
    @respx.mock
    async def test_call_openrouter_handles_malformed_response(self):
        """Неверный формат ответа вызывает исключение"""
        url = f"{settings.OPENROUTER_BASE_URL}/chat/completions"
        respx.post(url).mock(return_value=Response(200, json={"unexpected": "format"}))
        with pytest.raises(Exception):
            await call_openrouter("test prompt")

    @pytest.mark.asyncio
    @respx.mock
    async def test_call_openrouter_handles_missing_choices(self):
        """Ответ без поля choices вызывает исключение"""
        url = f"{settings.OPENROUTER_BASE_URL}/chat/completions"
        respx.post(url).mock(return_value=Response(200, json={"choices": []}))
        with pytest.raises(Exception):
            await call_openrouter("test prompt")

    @pytest.mark.asyncio
    @respx.mock
    async def test_call_openrouter_sets_correct_headers(self):
        """Проверяет, что заголовки запроса установлены правильно"""
        url = f"{settings.OPENROUTER_BASE_URL}/chat/completions"
        respx.post(url).mock(return_value=Response(200, json={
            "choices": [{"message": {"content": "Ответ"}}]
        }))
        await call_openrouter("test")
        request = respx.post(url).calls.last
        headers = request.request.headers
        assert "Authorization" in headers
        assert headers["Authorization"] == f"Bearer {settings.OPENROUTER_API_KEY}"
        assert headers["Content-Type"] == "application/json"

    @pytest.mark.asyncio
    @respx.mock
    async def test_call_openrouter_handles_http_error(self):
        """Ошибка HTTP (не 200) вызывает исключение"""
        url = f"{settings.OPENROUTER_BASE_URL}/chat/completions"
        respx.post(url).mock(return_value=Response(500, text="Internal Server Error"))
        with pytest.raises(Exception) as exc_info:
            await call_openrouter("test prompt")
        assert "500" in str(exc_info.value) or "Internal Server Error" in str(exc_info.value)