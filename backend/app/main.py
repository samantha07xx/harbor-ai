from fastapi import FastAPI

from app.api import health, knowledge_base, prepare
from app.config import APP_NAME

app = FastAPI(title=APP_NAME)

app.include_router(health.router, prefix="/api")
app.include_router(prepare.router, prefix="/api")
app.include_router(knowledge_base.router, prefix="/api")