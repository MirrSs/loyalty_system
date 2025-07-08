from fastapi import APIRouter, Depends, Request, Response
from db.managers.config_managers import ConfigManager
from db.base import MongoManager, get_database
from schemas.config_schemas import ModuleConfig
from manager import BotManager, get_bot_manager
from aiogram.types import Update
from loguru import logger

webhook_router = APIRouter(tags=["webhook"])


@webhook_router.post("/webhook/{client_id}/{config_id}")
async def telegram_api_webhook(
    client_id: str,
    config_id: str,
    request: Request,
    session: MongoManager = Depends(get_database),
    bot_manager: BotManager = Depends(get_bot_manager),
):
    try:
        config = await ConfigManager.retrieve(
            db=session,
            client_id=client_id,
            config_id=config_id,
        )
        if not config:
            logger.error(
                f"Config not found for client_id={client_id}, config_id={config_id}"
            )
            return Response(status_code=404, content="Config not found")

        config = ModuleConfig(**config)
        bot = bot_manager.bots.get(config.telegram_token)

        if not bot:
            logger.error(f"Bot not found for token={config.telegram_token}")
            return Response(status_code=404, content="Bot not found")

        dp = bot_manager.dispatchers.get(config.telegram_token)
        update_data = await request.json()
        update = Update.model_validate(update_data, context={"bot": bot})

        response = await dp.feed_update(bot, update)
        return Response(status_code=200, content=response)

    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        return Response(status_code=200)
