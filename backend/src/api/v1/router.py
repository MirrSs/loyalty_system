from fastapi import APIRouter

from api.v1.config_router import config_router
from api.v1.webhook_router import webhook_router
from api.v1.customer_router import customer_router

api_v1 = APIRouter(prefix="/v1")

# Add your routers here
api_v1.include_router(config_router)
api_v1.include_router(webhook_router)
api_v1.include_router(customer_router)
