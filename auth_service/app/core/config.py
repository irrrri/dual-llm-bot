from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Конфигурация приложения: имя, окружение, JWT настройки, путь к БД"""
    APP_NAME: str = "auth-service"
    ENV: str = "local"
    JWT_SECRET: str = "change_me_super_secret"
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    SQLITE_PATH: str = "./auth.db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
