import httpx
from aiogram import Router, F
from aiogram.types import Message
from schemas.config_schemas import ModuleConfig
from db.base import MongoManager, get_database
from core.customer import Customer

from loguru import logger


def register_handlers(router: Router, config: ModuleConfig):
    transport_router = Router()

    @transport_router.message(F.text)
    async def send_transport_message(
        message: Message,
    ):
        session: MongoManager = await get_database()
        customer = await Customer.load(
            chat_id=message.chat.id, config=config, session=session
        )
        if not customer:
            await message.answer("Клиент не найден. Возможно вы не прошли авторизацию")
            return
        if message.text:
            await message.answer(f"ECHO: {message.text}")

    router.include_router(transport_router)
