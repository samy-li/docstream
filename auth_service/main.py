from fastapi import FastAPI
from app.api.routes import get_router

app = FastAPI()
router = get_router()
app.include_router(router)
