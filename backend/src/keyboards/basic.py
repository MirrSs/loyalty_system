from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types
from schemas.config_schemas import ModuleConfig


async def get_basic_keyboard(config: ModuleConfig):
    if config.buttons:
        if config.buttons.main:
            _builder = ReplyKeyboardBuilder()
            if config.buttons.main.get_profile.show:
                _builder.row(
                    types.KeyboardButton(text=config.buttons.main.get_profile.text)
                )
            if config.buttons.main.get_loyalty_actions.show:
                _builder.row(
                    types.KeyboardButton(
                        text=config.buttons.main.get_loyalty_actions.text
                    )
                )
            return _builder.as_markup(resize_keyboard=True)
    return None
