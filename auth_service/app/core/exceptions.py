from fastapi import HTTPException, status

class AppHTTPException(HTTPException):
    """Базовое исключение для всех HTTP ошибок приложения"""
    pass

class UserAlreadyExistsError(AppHTTPException):
    """Ошибка 409: пользователь с таким email уже существует"""
    def __init__(self):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

class InvalidCredentialsError(AppHTTPException):
    """Ошибка 401: неверный email или пароль"""
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

class InvalidTokenError(AppHTTPException):
    """Ошибка 401: неверный формат токена"""
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

class UserNotFoundError(AppHTTPException):
    """Ошибка 404: пользователь не найден"""
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
class TokenExpiredError(AppHTTPException):
    """Ошибка 401: срок действия токена истек"""
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")

class PermissionDeniedError(AppHTTPException):
    """Ошибка 403: недостаточно прав для выполнения операции"""
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")