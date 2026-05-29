import pytest
from jose import jwt
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.core.jwt import decode_and_validate


class TestJWTValidation:
    """Тесты валидации JWT токенов в Bot Service"""
    def test_decode_valid_token_returns_payload(self):
        """Декодирование валидного токена возвращает payload с sub"""
        payload = {
            "sub": "1",
            "role": "user",
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        }
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
        result = decode_and_validate(token)
        assert result is not None
        assert "sub" in result
        assert result["sub"] == "1"

    def test_decode_invalid_token_raises_error(self):
        """Мусорная строка вместо токена вызывает ValueError."""
        with pytest.raises(ValueError, match="Invalid token"):
            decode_and_validate("not.a.valid.jwt.token")

    def test_decode_malformed_token_raises_error(self):
        """Битый токен вызывает ValueError."""
        with pytest.raises(ValueError):
            decode_and_validate("malformed")

    def test_decode_empty_token_raises_error(self):
        """Пустой токен вызывает ValueError"""
        with pytest.raises(ValueError):
            decode_and_validate("")

    def test_decode_expired_token_raises_error(self):
        """Истекший токен вызывает ValueError с сообщением 'Token expired'"""
        payload = {
            "sub": "1",
            "role": "user",
            "iat": datetime.now(timezone.utc) - timedelta(hours=2),
            "exp": datetime.now(timezone.utc) - timedelta(hours=1)
        }
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
        with pytest.raises(ValueError, match="Token expired"):
            decode_and_validate(token)