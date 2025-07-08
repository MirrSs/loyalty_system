from pydantic import BaseModel, Field
from typing import Optional, Dict


class ActionButton(BaseModel):
    show: bool
    text: str


class MainButtons(BaseModel):
    get_profile: Optional[ActionButton] = ActionButton(show=False, text="Профиль")
    get_loyalty_actions: Optional[ActionButton] = ActionButton(
        show=False, text="Действия с баллами"
    )


class Buttons(BaseModel):
    main: Optional[MainButtons] = MainButtons()


class QRData(BaseModel):
    first_name: Optional[bool] = None
    last_name: Optional[bool] = None
    phone: Optional[bool] = None
    chat_id: Optional[bool] = None


class LoyaltyLevel(BaseModel):
    title: str
    privilegeSize: Optional[float] = Field(
        None, description="Размер скидки, процент или курс начисления бонусов"
    )
    privilegeSizePromo: Optional[float] = Field(
        None,
        description="Размер скидки, процент или курс начисления бонусов для акционных товаров",
    )


class ModuleConfig(BaseModel):
    client_id: str
    config_id: str

    name: str

    telegram_token: str

    start_message: Optional[str] = None

    show_user_consent: Optional[bool] = False
    user_consent_link: Optional[str] = None
    privacy_policy_link: Optional[str] = None

    order_pagination_size: Optional[int] = 10

    allow_loyalty: Optional[bool] = False
    loyalty_pagination_size: Optional[int] = 10

    qr_data: Optional[QRData] = None

    levels: Dict[str, LoyaltyLevel] = {
        "default": LoyaltyLevel(
            title="Стандартный", privilegeSize=0.0, privilegeSizePromo=0.0
        )
    }

    buttons: Optional[Buttons] = None
