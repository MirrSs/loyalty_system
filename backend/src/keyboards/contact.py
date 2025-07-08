from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types


_builder = ReplyKeyboardBuilder()
_builder.row(types.KeyboardButton(text="Отправить контакт", request_contact=True))

get_contact_keyboard = _builder
