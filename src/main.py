from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.routes import base, data
# asynccontextmanager is a Python utility that lets you create a function with two phases:
from motor.motor_asyncio import AsyncIOMotorClient
from src.helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    settings = get_settings()

    app.state.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.state.db_client = app.state.mongo_conn[settings.MONGODB_DATABASE]
    
    llm_provider_factory = LLMProviderFactory(settings)
    # generation_client 
    app.state.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.state.generation_client.set_generation_model(model_id= settings.GENEATION_MODEL_ID)
    
    # embedding_client 
    app.state.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.state.embedding_client.set_generation_model(model_id= settings.EMBEDDING_MODEL_ID,
                                                    embedding_size=settings.EMBEDDING_MODEL_SIZE)

    yield

    # Shutdown
    app.state.mongo_conn.close()
    
app = FastAPI(lifespan=lifespan)
app.include_router(base.base_router)
app.include_router(data.data_router)

