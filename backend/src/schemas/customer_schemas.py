from pydantic import BaseModel
from typing import Optional
from .basic_schemas import BasicResponse
from schemas.config_schemas import LoyaltyLevel


class CustomerSchema(BaseModel):
    chat_id: int
    client_id: str
    config_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    balance: int = 0
    level_id: str = "default"
    level: LoyaltyLevel


class ResponseGetCustomer(BasicResponse):
    customer: Optional[CustomerSchema] = None


class RequestChangeBalance(BaseModel):
    chat_id: int
    amount: int
    comment: Optional[str] = None


class RequestChangeLevel(BaseModel):
    chat_id: int
    level: str
