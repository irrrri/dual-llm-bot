import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.usecases.auth import AuthUsecase


class TestAuthUsecase:
    """Тесты бизнес-логики аутентификации"""

    @pytest.fixture
    def mock_repo(self):
        """Создает мок репозитория"""
        repo = AsyncMock()
        repo.get_by_email = AsyncMock()
        repo.get_by_id = AsyncMock()
        repo.create = AsyncMock()
        return repo

    @pytest.fixture
    def auth_uc(self, mock_repo):
        """Создает usecase с мок-репозиторием"""
        return AuthUsecase(mock_repo)

    @pytest.mark.asyncio
    async def test_register_success(self, auth_uc, mock_repo):
        """Успешная регистрация нового пользователя"""
        mock_repo.get_by_email.return_value = None
        mock_repo.create.return_value = MagicMock(id=1, email="new@example.com")
        user = await auth_uc.register("new@example.com", "password123")
        assert user is not None
        mock_repo.get_by_email.assert_called_once_with("new@example.com")
        mock_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_user_already_exists(self, auth_uc, mock_repo):
        """Регистрация существующего пользователя вызывает ошибку"""
        mock_repo.get_by_email.return_value = MagicMock()
        with pytest.raises(UserAlreadyExistsError):
            await auth_uc.register("exists@example.com", "password")

    @pytest.mark.asyncio
    async def test_login_success(self, auth_uc, mock_repo):
        """Успешный вход пользователя"""
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.role = "user"
        mock_user.password_hash = "$2b$12$..."
        mock_repo.get_by_email.return_value = mock_user
        with patch("app.usecases.auth.verify_password", return_value=True):
            token = await auth_uc.login("user@example.com", "correct")
        assert token is not None
        assert isinstance(token, str)
        mock_repo.get_by_email.assert_called_once_with("user@example.com")

    @pytest.mark.asyncio
    async def test_login_invalid_credentials_wrong_password(self, auth_uc, mock_repo):
        """Неверный пароль вызывает ошибку"""
        mock_user = MagicMock()
        mock_user.password_hash = "hash"
        mock_repo.get_by_email.return_value = mock_user
        with patch("app.usecases.auth.verify_password", return_value=False):
            with pytest.raises(InvalidCredentialsError):
                await auth_uc.login("user@example.com", "wrong")

    @pytest.mark.asyncio
    async def test_login_user_not_found(self, auth_uc, mock_repo):
        """Несуществующий пользователь вызывает ошибку"""
        mock_repo.get_by_email.return_value = None
        with pytest.raises(InvalidCredentialsError):
            await auth_uc.login("nonexistent@example.com", "password")

    @pytest.mark.asyncio
    async def test_me_success(self, auth_uc, mock_repo):
        """Получение профиля существующего пользователя"""
        mock_user = MagicMock(id=1, email="user@example.com", role="user")
        mock_repo.get_by_id.return_value = mock_user
        user = await auth_uc.me(1)
        assert user == mock_user
        mock_repo.get_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_me_user_not_found(self, auth_uc, mock_repo):
        """Получение профиля несуществующего пользователя вызывает ошибку"""
        mock_repo.get_by_id.return_value = None
        with pytest.raises(UserNotFoundError):
            await auth_uc.me(99999)