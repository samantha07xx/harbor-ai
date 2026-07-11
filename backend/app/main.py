from fastapi import FastAPI

from app.api import health

app = FastAPI(title="Harbor AI API")

app.include_router(health.router, prefix="/api")