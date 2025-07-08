import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
import os
from loguru import logger
from db.base import db
from settings import (
    MONGODB_PROD_URL,
    MONGODB_PROD_USER,
    MONGODB_PROD_PASSWORD,
    MONGODB_DEV_URL,
)
from manager import BotManager
from fastapi.middleware.cors import CORSMiddleware
from api.base_router import api_router
from db.managers.config_managers import ConfigManager
from db.base import MongoManager, get_database
from schemas.config_schemas import ModuleConfig

from services.scheduler.scheduler import scheduler

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "https://web.telegram.org",
    "https://webapp.telegram.org*",
]


async def load_configs() -> list[ModuleConfig]:
    session: MongoManager = await get_database()
    db_configs = await ConfigManager.list(db=session)
    return [ModuleConfig(**config) for config in db_configs]


@asynccontextmanager
async def lifespan(application: FastAPI):
    # Mongo connection
    if os.getenv("ENVIROMENT") == "DEV":
        await db.connect_to_database(path=MONGODB_DEV_URL)
    elif os.getenv("ENVIROMENT") == "PRODUCTION":
        await db.connect_to_database(
            path=MONGODB_PROD_URL,
            user=MONGODB_PROD_USER,
            password=MONGODB_PROD_PASSWORD,
        )
    # Starting bot
    logger.info("🚀 Starting application")

    bot_manager = BotManager(await load_configs())
    asyncio.create_task(bot_manager.start_all())  # Запуск в фоне

    yield
    logger.info("⛔ Stopping application")
    await db.close_database_connection()
    await bot_manager.stop_all()


app = FastAPI(lifespan=lifespan)

app.include_router(api_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scheduler.start()


@app.get("/ping/")
async def healthcheck():
    return {"ping": "pong!"}
