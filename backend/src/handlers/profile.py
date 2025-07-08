from aiogram.types import BufferedInputFile
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from schemas.config_schemas import ModuleConfig
from db.base import MongoManager, get_database
from core.customer import Customer
from services.bot.profile import ProfileService
from aiogram.utils.keyboard import InlineKeyboardBuilder


def register_handlers(router: Router, config: ModuleConfig):
    profile_router = Router()

    @profile_router.message(
        F.text == config.buttons.main.get_profile.text
        if config.buttons.main
        else "Профиль"
    )
    async def get_customer_profile(
        message: Message,
    ):
        session: MongoManager = await get_database()
        customer: Customer = await Customer.load(
            chat_id=message.chat.id, config=config, session=session
        )

        if not customer:
            await message.answer("Клиент не найден. Возможно вы не прошли авторизацию")
            return

        response_messages = f"{config.name}\n"

        if config.allow_loyalty:
            response_messages += f"<b>Баланс бонусных баллов</b>: {customer.balance}\n"
            if customer.level_id:
                if customer.level:
                    response_messages += f"\n<b>Уровень</b>: {customer.level.title}\n"
                    response_messages += f"{customer.level.privilegeSize}% за товары/услуги по обычной цене\n"
                    response_messages += f"{customer.level.privilegeSizePromo}% за товары/услуги по акционной цене\n"

            if customer:
                builder = InlineKeyboardBuilder()
                builder.button(text="Закрыть", callback_data="profile_close")
                qr_code = await ProfileService.get_qr(config=config, customer=customer)
                await message.answer_photo(
                    photo=BufferedInputFile(qr_code.getvalue(), filename="qrcode.png"),
                    caption=response_messages,
                    reply_markup=builder.as_markup(),
                )
                return
        await message.answer(response_messages)

    @profile_router.callback_query(F.data == "profile_close")
    async def close_orders(callback: CallbackQuery):
        await callback.message.delete()
        await callback.answer()

    router.include_router(profile_router)
