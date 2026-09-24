from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.routes import base, data
# asynccontextmanager is a Python utility that lets you create a function with two phases:
from motor.motor_asyncio import AsyncIOMotorClient
from src.helpers.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    settings = get_settings()

    app.state.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.state.db_client = app.state.mongo_conn[settings.MONGODB_DATABASE]

    yield

    # Shutdown
    app.state.mongo_conn.close()
    
app = FastAPI(lifespan=lifespan)
app.include_router(base.base_router)
app.include_router(data.data_router)