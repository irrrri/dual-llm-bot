from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    """Схема запроса на регистрацию: email и пароль"""
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    """Схема ответа с JWT токеном"""
    access_token: str
    token_type: str = "bearer"