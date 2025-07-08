from typing import Union
from aiogram.types import Message, CallbackQuery
from schemas.loyalty_schemas import LoyaltyAction
from schemas.config_schemas import ModuleConfig

from aiogram.utils.keyboard import InlineKeyboardBuilder


class LoyaltyService:
    @classmethod
    def get_operation_display_name(cls, operation: LoyaltyAction) -> str:
        """Формирует отображаемое название операции"""
        operation_type = "Начисление" if operation.amount > 0 else "Списание"
        date_str = operation.created_at.strftime("%d.%m.%Y в %H:%M")
        return f"{operation_type} {date_str}"

    @classmethod
    async def show_paginated_list(
        cls,
        message: Union[Message, CallbackQuery],
        operations: list[LoyaltyAction],
        page: int,
        config: ModuleConfig,
    ):
        """Показывает страницу со списком операций"""
        start_index = page * config.loyalty_pagination_size
        end_index = start_index + config.loyalty_pagination_size
        page_operations = operations[start_index:end_index]
        total_pages = (
            len(operations) + config.loyalty_pagination_size - 1
        ) // config.loyalty_pagination_size

        builder = InlineKeyboardBuilder()

        # Кнопки операций
        for i, operation in enumerate(page_operations):
            builder.button(
                text=cls.get_operation_display_name(operation),
                callback_data=f"loyalty_detail_{start_index + i}",
            )

        # Пагинация
        pagination_builder = InlineKeyboardBuilder()

        if page > 0:
            pagination_builder.button(
                text="← Назад", callback_data=f"loyalty_page_{page - 1}"
            )

        pagination_builder.button(
            text=f"{page + 1}/{total_pages}", callback_data="no_action"
        )

        if page < total_pages - 1:
            pagination_builder.button(
                text="Вперед →", callback_data=f"loyalty_page_{page + 1}"
            )

        builder.adjust(1)
        pagination_builder.adjust(3)
        pagination_builder.button(text="Закрыть", callback_data="loyalty_close_list")
        builder.attach(pagination_builder)

        text = "📋 <b>Ваши операции по бонусному счету</b>\nВыберите операцию для просмотра деталей:"

        if isinstance(message, CallbackQuery):
            await message.message.edit_text(text, reply_markup=builder.as_markup())
            await message.answer()
        else:
            await message.answer(text, reply_markup=builder.as_markup())

    @classmethod
    async def show_operation_detail(
        cls,
        message: Union[Message, CallbackQuery],
        operation: LoyaltyAction,
    ):
        """Показывает детали одной операции"""
        text = (
            f"<b>{cls.get_operation_display_name(operation=operation)}</b>\n"
            f"<b>Сумма:</b> {abs(operation.amount)} бонусов\n"
        )

        if operation.comment:
            text += f"<b>Комментарий:</b> {operation.comment}\n"

        builder = InlineKeyboardBuilder()
        builder.button(text="← Назад к списку", callback_data="back_to_operations")

        if isinstance(message, CallbackQuery):
            await message.message.edit_text(text, reply_markup=builder.as_markup())
            await message.answer()
        else:
            await message.answer(text, reply_markup=builder.as_markup())
