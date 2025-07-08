from fastapi import APIRouter, Depends, HTTPException
from db.managers.config_managers import ConfigManager
from db.base import MongoManager, get_database
from schemas.config_schemas import ModuleConfig
from manager import BotManager, get_bot_manager
from loguru import logger

config_router = APIRouter(tags=["config"])


@config_router.get("/configs", response_model=ModuleConfig)
async def get_config(config_id: str, session: MongoManager = Depends(get_database)):
    return await ConfigManager.retrieve(db=session, config_id=config_id)


@config_router.patch("/configs/{config_id}/restart", response_model=ModuleConfig)
async def restart_bot_instance(
    config_id: str,
    session: MongoManager = Depends(get_database),
    bot_manager: BotManager = Depends(get_bot_manager),
):
    # Получаем обновленную конфигурацию из БД
    config_data = await ConfigManager.retrieve(db=session, config_id=config_id)
    if not config_data:
        raise HTTPException(status_code=404, detail="Config not found")

    config = ModuleConfig(**config_data)

    # Перезапускаем бота (включая обновление конфига)
    success = await bot_manager.restart_bot(config)
    if not success:
        raise HTTPException(
            status_code=500, detail="Failed to restart bot with new config"
        )

    logger.success(f"Bot {config_id} restarted successfully")
    return config
