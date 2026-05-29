import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.core.config import settings

class TestTokenCommand:
    """Тесты команды /token"""

    @pytest.mark.asyncio
    async def test_token_command_saves_to_redis(self, fake_redis_client):
        """Команда /token сохраняет токен в Redis"""
        payload = {
            "sub": "1",
            "role": "user",
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        }
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
        mock_message = AsyncMock()
        mock_message.from_user.id = 12345
        mock_message.text = f"/token {token}"
        mock_message.answer = AsyncMock()
        with patch("app.bot.handlers.get_redis", return_value=fake_redis_client):
            from app.bot.handlers import cmd_token
            await cmd_token(mock_message)
        expected_key = f"token:{mock_message.from_user.id}"
        saved_token = await fake_redis_client.get(expected_key)
        assert saved_token == token
        mock_message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_token_command_invalid_format(self, fake_redis_client):
        """Неверный формат команды /token вызывает сообщение об ошибке"""
        mock_message = AsyncMock()
        mock_message.text = "/token"
        mock_message.answer = AsyncMock()
        with patch("app.bot.handlers.get_redis", return_value=fake_redis_client):
            from app.bot.handlers import cmd_token
            await cmd_token(mock_message)
        mock_message.answer.assert_called_once()
        assert "использование" in mock_message.answer.call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_token_command_invalid_token(self, fake_redis_client):
        """Невалидный токен вызывает сообщение об ошибке"""
        mock_message = AsyncMock()
        mock_message.text = "/token invalid.token.string"
        mock_message.answer = AsyncMock()
        with patch("app.bot.handlers.get_redis", return_value=fake_redis_client):
            from app.bot.handlers import cmd_token
            await cmd_token(mock_message)
        mock_message.answer.assert_called_once()
        assert "невалиден" in mock_message.answer.call_args[0][0].lower()


class TestHandleText:
    """Тесты обработки текстовых сообщений"""

    @pytest.mark.asyncio
    async def test_handle_text_without_token(self, fake_redis_client):
        """Без токена бот отказывает в доступе, Celery не вызывается"""
        mock_message = AsyncMock()
        mock_message.from_user.id = 12345
        mock_message.chat.id = 12345
        mock_message.text = "test"
        mock_message.answer = AsyncMock()
        with patch("app.bot.handlers.get_redis", return_value=fake_redis_client):
            with patch("app.tasks.llm_tasks.llm_request.delay") as mock_delay:
                from app.bot.handlers import handle_text
                await handle_text(mock_message)
        mock_delay.assert_not_called()
        mock_message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_text_with_valid_token_calls_celery(self, fake_redis_client):
        """С валидным токеном бот вызывает Celery"""
        payload = {
            "sub": "1",
            "role": "user",
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        }
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
        mock_message = AsyncMock()
        mock_message.from_user.id = 12345
        mock_message.chat.id = 12345
        mock_message.text = "test question"
        mock_message.answer = AsyncMock()
        await fake_redis_client.set(f"token:{mock_message.from_user.id}", token)
        with patch("app.bot.handlers.get_redis", return_value=fake_redis_client):
            with patch("app.tasks.llm_tasks.llm_request.delay") as mock_delay:
                with patch("app.core.jwt.decode_and_validate", return_value={"sub": "1"}):
                    from app.bot.handlers import handle_text
                    await handle_text(mock_message)
        mock_delay.assert_called_once_with(mock_message.chat.id, mock_message.text)
        mock_message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_text_with_expired_token(self, fake_redis_client, test_jwt_token_expired):
        """С истекшим токеном бот отказывает в доступе"""
        mock_message = AsyncMock()
        mock_message.from_user.id = 12345
        mock_message.chat.id = 12345
        mock_message.text = "test question"
        mock_message.answer = AsyncMock()
        await fake_redis_client.set(f"token:{mock_message.from_user.id}", test_jwt_token_expired)
        with patch("app.bot.handlers.get_redis", return_value=fake_redis_client):
            with patch("app.tasks.llm_tasks.llm_request.delay") as mock_delay:
                from app.bot.handlers import handle_text
                await handle_text(mock_message)
        mock_delay.assert_not_called()
        mock_message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_command(self, fake_redis_client):
        """Команда /start отправляет приветственное сообщение"""
        mock_message = AsyncMock()
        mock_message.answer = AsyncMock()
        from app.bot.handlers import cmd_start
        await cmd_start(mock_message)
        mock_message.answer.assert_called_once()
