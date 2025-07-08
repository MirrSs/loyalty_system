from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LoyaltyAction(BaseModel):
    client_id: str
    config_id: str
    chat_id: int
    amount: int
    created_at: Optional[datetime] = Field(
        datetime.now(),
        description="Дата и время проведения операции. Если не указать, то будет использоваться текущее время сервера.",
    )
    comment: Optional[str] = None
