from fastapi import FastAPI

app = FastAPI(title="Bot Service")

@app.get("/health")
async def health():
    """Проверка работоспособности сервиса"""
    return {"status": "ok"}