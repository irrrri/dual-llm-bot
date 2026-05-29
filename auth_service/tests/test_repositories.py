import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.users import UserRepository


class TestUserRepository:
    """Тесты репозитория пользователей"""

    @pytest.mark.asyncio
    async def test_create_user(self, async_session: AsyncSession):
        """Создание пользователя сохраняет его в БД"""
        repo = UserRepository(async_session)
        email = "test@example.com"
        password_hash = "hashed_password"
        user = await repo.create(email, password_hash, role="user")
        assert user.id is not None
        assert user.email == email
        assert user.password_hash == password_hash
        assert user.role == "user"

    @pytest.mark.asyncio
    async def test_get_by_email_found(self, async_session: AsyncSession):
        """Поиск пользователя по email возвращает пользователя"""
        repo = UserRepository(async_session)
        email = "found@example.com"
        await repo.create(email, "hash", "user")
        user = await repo.get_by_email(email)
        assert user is not None
        assert user.email == email

    @pytest.mark.asyncio
    async def test_get_by_email_not_found(self, async_session: AsyncSession):
        """Поиск несуществующего email возвращает None"""
        repo = UserRepository(async_session)
        user = await repo.get_by_email("nonexistent@example.com")
        assert user is None

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, async_session: AsyncSession):
        """Поиск пользователя по id возвращает пользователя"""
        repo = UserRepository(async_session)
        created = await repo.create("test@example.com", "hash", "user")
        user = await repo.get_by_id(created.id)
        assert user is not None
        assert user.id == created.id
        assert user.email == created.email

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, async_session: AsyncSession):
        """Поиск несуществующего id возвращает None"""
        repo = UserRepository(async_session)
        user = await repo.get_by_id(99999)
        assert user is None