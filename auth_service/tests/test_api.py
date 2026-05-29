import pytest
from httpx import AsyncClient


class TestAuthAPI:
    """Интеграционные тесты эндпоинтов аутентификации."""

    @pytest.mark.asyncio
    async def test_register_success(self, async_client: AsyncClient):
        """Успешная регистрация пользователя"""
        response = await async_client.post(
            "/auth/register",
            json={"email": "test@example.com", "password": "testpass123"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "id" in data
        assert "role" in data
        assert "created_at" in data
        assert "password" not in data

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, async_client: AsyncClient):
        """Повторная регистрация с тем же email возвращает 409"""
        await async_client.post(
            "/auth/register",
            json={"email": "duplicate@example.com", "password": "pass123"}
        )
        response = await async_client.post(
            "/auth/register",
            json={"email": "duplicate@example.com", "password": "pass456"}
        )
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, async_client: AsyncClient):
        """Регистрация с невалидным email возвращает ошибку валидации"""
        response = await async_client.post(
            "/auth/register",
            json={"email": "not-an-email", "password": "pass123"}
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_login_success(self, async_client: AsyncClient):
        """Успешный вход возвращает JWT токен"""
        await async_client.post(
            "/auth/register",
            json={"email": "login@example.com", "password": "loginpass"}
        )
        response = await async_client.post(
            "/auth/login",
            data={"username": "login@example.com", "password": "loginpass"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0

    @pytest.mark.asyncio
    async def test_login_invalid_credentials_wrong_password(self, async_client: AsyncClient):
        """Вход с неверным паролем возвращает 401"""
        await async_client.post(
            "/auth/register",
            json={"email": "wrongpass@example.com", "password": "correctpass"}
        )
        response = await async_client.post(
            "/auth/login",
            data={"username": "wrongpass@example.com", "password": "wrongpass"}
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_user_not_found(self, async_client: AsyncClient):
        """Вход с несуществующим email возвращает 401"""
        response = await async_client.post(
            "/auth/login",
            data={"username": "nonexistent@example.com", "password": "anypass"}
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_me_with_valid_token(self, async_client: AsyncClient):
        """GET /auth/me с валидным токеном возвращает профиль"""
        await async_client.post(
            "/auth/register",
            json={"email": "me@example.com", "password": "mepass"}
        )
        login_response = await async_client.post(
            "/auth/login",
            data={"username": "me@example.com", "password": "mepass"}
        )
        token = login_response.json()["access_token"]
        response = await async_client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "me@example.com"
        assert "id" in data
        assert "role" in data

    @pytest.mark.asyncio
    async def test_me_without_token(self, async_client: AsyncClient):
        """GET /auth/me без токена возвращает 401"""
        response = await async_client.get("/auth/me")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_me_with_invalid_token(self, async_client: AsyncClient):
        """GET /auth/me с неверным токеном возвращает 401"""
        response = await async_client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid.token.string"}
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_health_endpoint(self, async_client: AsyncClient):
        """Проверка эндпоинта health"""
        response = await async_client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    @pytest.mark.asyncio
    async def test_full_user_flow(self, async_client: AsyncClient):
        """Полный сценарий: регистрация, логин, получение профиля"""
        email = "fullflow@example.com"
        password = "flowpass"
        reg_response = await async_client.post(
            "/auth/register",
            json={"email": email, "password": password}
        )
        assert reg_response.status_code == 201
        user_id = reg_response.json()["id"]
        login_response = await async_client.post(
            "/auth/login",
            data={"username": email, "password": password}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        me_response = await async_client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert me_response.status_code == 200
        assert me_response.json()["id"] == user_id
        assert me_response.json()["email"] == email