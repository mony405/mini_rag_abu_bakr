from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.routes import base, data, nlp
# asynccontextmanager is a Python utility that lets you create a function with two phases.
from motor.motor_asyncio import AsyncIOMotorClient
from src.helpers.config import get_settings
from src.stores.llm.LLMProviderFactory import LLMProviderFactory
from src.stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from src.stores.llm.templates.template_parser import TemplateParser
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    settings = get_settings()
    # 
    app.state.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.state.db_client = app.state.mongo_conn[settings.MONGODB_DATABASE]
    # 
    llm_provider_factory = LLMProviderFactory(settings) # openai
    vectordb_provider_factory = VectorDBProviderFactory(settings) #qdrant
    # generation_client 
    app.state.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.state.generation_client.set_generation_model(model_id= settings.GENERATION_MODEL_ID)
    
    # embedding_client 
    app.state.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.state.embedding_client.set_embedding_model(model_id= settings.EMBEDDING_MODEL_ID,
                                                    embedding_size=settings.EMBEDDING_MODEL_SIZE)
    # vector db client
    app.state.vectordb_client = vectordb_provider_factory.create(
        provider=settings.VECTOR_DB_BACKEND
    )
    app.state.vectordb_client.connect()
    app.state.template_parser = TemplateParser(
        language=settings.PRIMARY_LANG,
        default_language=settings.DEFAULT_LANG,
    )

    yield

    # Shutdown
    app.state.mongo_conn.close()
    app.state.vectordb_client.disconnect()
    
app = FastAPI(lifespan=lifespan)
app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)

