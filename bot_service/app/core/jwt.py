from jose import jwt, JWTError, ExpiredSignatureError
from app.core.config import settings

def decode_and_validate(token: str) -> dict:
    """Декодирует и валидирует JWT токен. Возвращает payload или выбрасывает ValueError"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
        if not payload.get("sub"):
            raise ValueError("Token payload missing sub")
        if "exp" not in payload:
            raise ValueError("Token payload missing exp")
        return payload
    except ExpiredSignatureError:
        raise ValueError("Token expired")
    except JWTError:
        raise ValueError("Invalid token")
