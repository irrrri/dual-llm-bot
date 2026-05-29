import pytest
from datetime import datetime, timezone

from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.core.exceptions import InvalidTokenError
from app.core.config import settings


class TestPasswordHashing:
    """Тесты хеширования паролей"""

    def test_hash_password_returns_different_hash_for_same_password(self):
        """Хеш не должен быть равен исходному паролю"""
        password = "my_secret_password"
        hashed = hash_password(password)
        assert hashed != password
        assert isinstance(hashed, str)

    def test_hash_password_returns_different_hashes_for_same_password(self):
        """Один и тот же пароль дает разные хеши"""
        password = "my_secret_password"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2

    def test_verify_password_correct(self):
        """Проверка правильного пароля возвращает True"""
        password = "correct_password"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Проверка неправильного пароля возвращает False"""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = hash_password(password)
        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty_string(self):
        """Проверка пустого пароля"""
        password = ""
        hashed = hash_password(password)
        assert verify_password("", hashed) is True
        assert verify_password("not_empty", hashed) is False


class TestJWT:
    """Тесты создания и валидации JWT токенов"""

    def test_create_access_token_contains_required_fields(self):
        """Токен должен содержать sub, role, iat, exp"""
        token_data = {"sub": "1", "role": "user"}
        token = create_access_token(token_data)
        payload = decode_token(token)
        assert payload["sub"] == "1"
        assert payload["role"] == "user"
        assert "iat" in payload
        assert "exp" in payload

    def test_create_access_token_iat_and_exp_correct(self):
        """Проверка, что iat и exp установлены правильно"""
        token_data = {"sub": "1", "role": "user"}
        now = datetime.now(timezone.utc)
        expected_iat = int(now.timestamp())
        expected_exp = expected_iat + (settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        token = create_access_token(token_data)
        payload = decode_token(token)
        assert abs(payload["iat"] - expected_iat) <= 5
        assert abs(payload["exp"] - expected_exp) <= 5

    def test_decode_valid_token_returns_payload(self):
        """Декодирование валидного токена возвращает payload"""
        token_data = {"sub": "42", "role": "admin"}
        token = create_access_token(token_data)
        payload = decode_token(token)
        assert payload["sub"] == "42"
        assert payload["role"] == "admin"

    def test_decode_invalid_token_raises_error(self):
        """Декодирование невалидного токена вызывает InvalidTokenError"""
        with pytest.raises(InvalidTokenError):
            decode_token("invalid.token.string")

    def test_decode_malformed_token_raises_error(self):
        """Декодирование битого токена вызывает InvalidTokenError"""
        with pytest.raises(InvalidTokenError):
            decode_token("not.a.jwt.token")

    def test_create_token_with_custom_data(self):
        """Токен может содержать дополнительные данные"""
        token_data = {"sub": "100", "role": "moderator", "custom_field": "value"}
        token = create_access_token(token_data)
        payload = decode_token(token)
        assert payload["sub"] == "100"
        assert payload["role"] == "moderator"
        assert payload["custom_field"] == "value"