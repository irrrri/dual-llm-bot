import pytest
from unittest.mock import AsyncMock
from datetime import datetime, timedelta, timezone
import fakeredis.aioredis
from app.core.config import settings


@pytest.fixture
def test_jwt_token():
    """Создает тестовый JWT токен"""
    from jose import jwt
    payload = {
        "sub": "1",
        "role": "user",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


@pytest.fixture
def test_jwt_token_expired():
    """Создает истекший JWT токен"""
    from jose import jwt
    payload = {
        "sub": "1",
        "role": "user",
        "iat": datetime.now(timezone.utc) - timedelta(hours=2),
        "exp": datetime.now(timezone.utc) - timedelta(hours=1)
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


@pytest.fixture
def mock_message():
    """Создает мок объекта Message из aiogram"""
    message = AsyncMock()
    message.from_user.id = 12345
    message.chat.id = 12345
    message.text = "test message"
    message.answer = AsyncMock()
    message.reply = AsyncMock()
    return message


@pytest.fixture
async def fake_redis_client():
    """Фикстура, возвращающая клиент FakeRedis"""
    redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    yield redis
    await redis.flushall()
    await redis.close()