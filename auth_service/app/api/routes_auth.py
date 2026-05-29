from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.usecases.auth import AuthUsecase
from app.api import deps
from app.schemas.auth import RegisterRequest, TokenResponse
from app.schemas.user import UserPublic

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserPublic, status_code=201)
async def register(
    register_data: RegisterRequest, 
    auth_uc: AuthUsecase = Depends(deps.get_auth_uc)
):
    """Регистрирует нового пользователя"""
    user = await auth_uc.register(register_data.email, register_data.password)
    return user

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    auth_uc: AuthUsecase = Depends(deps.get_auth_uc)
):
    """Аутентифицирует пользователя и возвращает JWT токен"""
    access_token = await auth_uc.login(form_data.username, form_data.password)
    return TokenResponse(access_token=access_token)

@router.get("/me", response_model=UserPublic)
async def me(
    user_id: int = Depends(deps.get_current_user_id), 
    auth_uc: AuthUsecase = Depends(deps.get_auth_uc)
):
    """Возвращает профиль текущего аутентифицированного пользователя"""
    user = await auth_uc.me(user_id)
    return user