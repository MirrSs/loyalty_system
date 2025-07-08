from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.command import Command
from schemas.config_schemas import ModuleConfig
from core.customer import Customer
from db.managers.customer_managers import CustomerManager

from keyboards.contact import get_contact_keyboard
from keyboards.basic import get_basic_keyboard
from db.base import MongoManager, get_database


class AuthState(StatesGroup):
    waiting_for_consent = State()
    waiting_for_contact = State()


def register_handlers(router: Router, config: ModuleConfig):
    start_router = Router()

    @start_router.message(Command("start"))
    async def command_start(message: Message, state: FSMContext):
        if config.show_user_consent:
            consent_text = (
                "Для того, чтобы мы могли продолжить общаться с вами, по законодательству, "
                f"нам нужно спросить у вас <a href='{config.user_consent_link}'>согласие на обработку персональных данных</a>.\n"
                f"Ознакомиться с нашей политикой конфиденциальности можно по ссылке <a href='{config.privacy_policy_link}'>здесь</a>."
            )

            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="✅ Даю согласие", callback_data="give_consent"
                        )
                    ]
                ]
            )

            await state.set_state(AuthState.waiting_for_consent)
            await message.answer(consent_text, reply_markup=keyboard)
        else:
            await state.set_state(AuthState.waiting_for_contact)
            await message.answer(
                f"{config.start_message if config.start_message else 'Добро пожаловать!'}",
                reply_markup=get_contact_keyboard.as_markup(resize_keyboard=True),
            )

    @start_router.callback_query(
        F.data == "give_consent", AuthState.waiting_for_consent
    )
    async def handle_consent(callback: CallbackQuery, state: FSMContext):
        await callback.message.edit_reply_markup(reply_markup=None)  # Убираем кнопку
        await state.set_state(AuthState.waiting_for_contact)
        await callback.message.answer(
            f"{config.start_message if config.start_message else 'Добро пожаловать!'}",
            reply_markup=get_contact_keyboard.as_markup(resize_keyboard=True),
        )
        await callback.answer()

    @start_router.message(AuthState.waiting_for_contact, F.contact)
    async def contact_handler(
        message: Message,
        state: FSMContext,
    ) -> None:
        session: MongoManager = await get_database()
        """
        Get contact info, then handle register
        """

        ### STAGE 1 - Search or Create customer, loyalty ###
        customer = await Customer.load(
            chat_id=message.chat.id, config=config, session=session
        )
        customer.phone = message.contact.phone_number
        customer.first_name = message.contact.first_name
        customer.last_name = message.contact.last_name
        customer.is_active = True
        if await CustomerManager.retrieve(
            db=session,
            chat_id=customer.chat_id,
            config_id=config.config_id,
            client_id=config.client_id,
        ):
            await customer.save(session=session)
        else:
            await CustomerManager.create(
                db=session, data=customer._dump(exclude={"level", "config"})
            )

        ### STAGE 2 - Welcome message ###
        await state.clear()
        await message.answer(
            "\n".join(
                filter(
                    None,
                    [
                        f"{customer.first_name}, выберите из меню информацию, которая вас сейчас интересует:",
                        f"\n🙂 {config.buttons.main.get_profile.text} - узнайте баланс бонусных баллов и ваш уровень лояльности. Покажите персональный QR-код кассиру, чтобы применить скидку по программе лояльности"
                        if config.buttons.main.get_profile.show
                        else None,
                        f"\n⭐️ {config.buttons.main.get_loyalty_actions.text} - узнайте историю начисления/списания ваших бонусных баллов"
                        if config.buttons.main.get_loyalty_actions.show
                        else None,
                    ],
                )
            ),
            reply_markup=await get_basic_keyboard(config),
        )

    @start_router.message(AuthState.waiting_for_contact)
    async def handle_other_messages_during_registration(message: Message):
        """Handling other actions during auth"""
        await message.answer(
            "Пожалуйста, отправьте ваш контакт для завершения регистрации."
        )

    @start_router.message(AuthState.waiting_for_consent)
    async def handle_other_messages_during_consent(message: Message):
        """Handling other actions during consent"""
        await message.answer(
            "Пожалуйста, нажмите кнопку <b>✅ Даю согласие</b> для продолжения."
        )

    router.include_router(start_router)
