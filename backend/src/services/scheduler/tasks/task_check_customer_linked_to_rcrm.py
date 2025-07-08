from loguru import logger
from db.base import get_database
from manager import BotManager, get_bot_manager
from db.managers.customer_managers import CustomerManager
from db.managers.config_managers import ConfigManager

from schemas.config_schemas import ModuleConfig
from core.customer import Customer

from aiogram.exceptions import TelegramForbiddenError
from aiogram import Bot


async def task_check_customer_active():
    logger.info("TASK Check customer activity: START")
    try:
        bot_manager: BotManager = get_bot_manager()
        session = await get_database()
        configs = [
            ModuleConfig(**config) for config in await ConfigManager.list(db=session)
        ]
        for config in configs:
            customers = await CustomerManager.list(
                db=session,
                config_id=config.config_id,
                client_id=config.client_id,
            )
            for customer in customers:
                customer = await Customer.load(
                    chat_id=customer.get("chat_id"), config=config, session=session
                )
                try:
                    if bot_manager.bots:
                        if bot_manager.bots.get(config.telegram_token):
                            bot: Bot = bot_manager.bots.get(config.telegram_token)
                            await bot.send_chat_action(
                                chat_id=customer.chat_id, action="typing"
                            )
                except TelegramForbiddenError as e:
                    logger.error(
                        f"TASK Check customer activity. client_id:{config.client_id}. chat_id:{customer.chat_id}. TelegramForbiddenError while handling message: {str(e)}"
                    )
                    customer.is_active = False
                    await customer.save(session=session)
    except Exception as e:
        logger.error(f"TASK Check customer activity. Error: {e}")
    finally:
        logger.info("TASK Check customer activity: FINISH")
