from pydantic import BaseModel
from datetime import datetime

class UserPublic(BaseModel):
    """Публичная информация о пользователе"""
    id: int
    email: str
    role: str
    created_at: datetime