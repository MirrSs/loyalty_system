from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from schemas.config_schemas import ModuleConfig
from db.base import MongoManager, get_database
from core.customer import Customer
from loguru import logger
from schemas.loyalty_schemas import LoyaltyAction
from services.bot.loyalty import LoyaltyService


def register_handlers(router: Router, config: ModuleConfig):
    loyalty_router = Router()

    @loyalty_router.message(
        F.text == config.buttons.main.get_loyalty_actions.text
        if config.buttons.main
        else "Активность"
    )
    async def get_loyalty_actions(
        message: Message,
        state: FSMContext,
    ):
        session: MongoManager = await get_database()
        customer: Customer = await Customer.load(
            chat_id=message.chat.id, config=config, session=session
        )
        if not customer:
            await message.answer("Клиент не найден. Возможно вы не прошли авторизацию")
            return

        if not config.allow_loyalty:
            await message.answer("Программа лояльности недоступна")
            return

        if not customer.level_id:
            await message.answer(
                "Уровень Программы лояльности отсутствует. Пройдите повторную регистрацию"
            )
            return

        actions = await customer.loyalty_actions(session=session)
        if not actions:
            await message.answer("Нет операций по бонусному счету")
            return

        # Сохраняем все операции и текущую страницу
        await state.update_data(
            all_operations=actions,
            current_page=0,
            current_operation=None,
        )

        # # Показываем первую страницу
        await LoyaltyService.show_paginated_list(
            message=message, operations=actions, page=0, config=config
        )

    @loyalty_router.callback_query(F.data.startswith("loyalty_page_"))
    async def change_loyalty_page(callback: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        all_operations = data.get("all_operations", [])

        try:
            page = int(callback.data.split("_")[2])
            await LoyaltyService.show_paginated_list(
                message=callback, operations=all_operations, page=page, config=config
            )
            await state.update_data(current_page=page)
        except Exception as e:
            logger.error(f"Error changing loyalty page: {e}")
            await callback.answer("Ошибка при переключении страниц")

    @loyalty_router.callback_query(F.data.startswith("loyalty_detail_"))
    async def show_loyalty_detail(
        callback: CallbackQuery,
        state: FSMContext,
    ):
        data = await state.get_data()
        all_operations = data.get("all_operations", [])

        try:
            operation_index = int(callback.data.split("_")[2])
            if 0 <= operation_index < len(all_operations):
                operation: LoyaltyAction = all_operations[operation_index]
                await LoyaltyService.show_operation_detail(
                    message=callback, operation=operation
                )
        except Exception as e:
            logger.error(f"Error showing loyalty detail: {e}")
            await callback.answer("Ошибка при показе операции")

    @loyalty_router.callback_query(F.data == "back_to_operations")
    async def back_to_operations(callback: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        all_operations = data.get("all_operations", [])
        current_page = data.get("current_page", 0)

        await LoyaltyService.show_paginated_list(
            message=callback,
            operations=all_operations,
            page=current_page,
            config=config,
        )

    @loyalty_router.callback_query(F.data == "loyalty_close_list")
    async def close_operations(callback: CallbackQuery):
        await callback.message.delete()
        await callback.answer()

    router.include_router(loyalty_router)
