from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Конфигурация бота"""
    APP_NAME: str = "bot-service"
    ENV: str = "local"

    TELEGRAM_BOT_TOKEN: str = ""

    JWT_SECRET: str = "change_me_super_secret"
    JWT_ALG: str = "HS256"

    REDIS_URL: str = "redis://redis:6379/0"
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672//"

    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "stepfun/step-3.5-flash:free"
    OPENROUTER_SITE_URL: str = "https://example.com"
    OPENROUTER_APP_NAME: str = "bot-service"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
