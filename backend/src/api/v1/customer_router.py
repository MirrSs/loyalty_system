from fastapi import APIRouter, Depends, HTTPException
from db.managers.config_managers import ConfigManager
from db.base import MongoManager, get_database
from schemas.config_schemas import ModuleConfig
from core.customer import Customer
from schemas.customer_schemas import (
    ResponseGetCustomer,
    RequestChangeLevel,
    RequestChangeBalance,
)
from loguru import logger
from fastapi.responses import Response

customer_router = APIRouter(tags=["customer"], prefix="/customers")


@customer_router.get(
    "/{client_id}/{config_id}/{chat_id}",
    response_model=ResponseGetCustomer,
)
async def get_customer(
    client_id: str,
    config_id: str,
    chat_id: int,
    response: Response,
    session: MongoManager = Depends(get_database),
):
    config_data = await ConfigManager.retrieve(
        db=session, client_id=client_id, config_id=config_id
    )
    if not config_data:
        response.status_code = 404
        return ResponseGetCustomer(success=False, error="Config not found")

    config = ModuleConfig(**config_data)
    customer = await Customer.load(chat_id=chat_id, config=config, session=session)
    if customer:
        return ResponseGetCustomer(success=True, customer=customer._dump())


@customer_router.post(
    "/{client_id}/{config_id}/balance",
    response_model=ResponseGetCustomer,
)
async def change_customer_balance(
    client_id: str,
    config_id: str,
    data: RequestChangeBalance,
    response: Response,
    session: MongoManager = Depends(get_database),
):
    config_data = await ConfigManager.retrieve(
        db=session, client_id=client_id, config_id=config_id
    )
    if not config_data:
        response.status_code = 404
        return ResponseGetCustomer(success=False, error="Config not found")

    config = ModuleConfig(**config_data)
    customer = await Customer.load(chat_id=data.chat_id, config=config, session=session)

    customer, error = await customer.change_balance(
        amount=data.amount, comment=data.comment, session=session
    )

    if error:
        response.status_code = 400
        return ResponseGetCustomer(success=False, error=error)

    return ResponseGetCustomer(success=True, customer=customer._dump())


@customer_router.post(
    "/{client_id}/{config_id}/level",
    response_model=ResponseGetCustomer,
)
async def change_customer_level(
    client_id: str,
    config_id: str,
    data: RequestChangeLevel,
    response: Response,
    session: MongoManager = Depends(get_database),
):
    config_data = await ConfigManager.retrieve(
        db=session, client_id=client_id, config_id=config_id
    )
    if not config_data:
        response.status_code = 404
        return ResponseGetCustomer(success=False, error="Config not found")

    config = ModuleConfig(**config_data)
    customer = await Customer.load(chat_id=data.chat_id, config=config, session=session)

    customer, error = await customer.change_level(level=data.level, session=session)

    if error:
        response.status_code = 400
        return ResponseGetCustomer(success=False, error=error)

    return ResponseGetCustomer(success=True, customer=customer._dump())
