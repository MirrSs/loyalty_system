from fastapi import APIRouter

from api.v1.router import api_v1

api_router = APIRouter(prefix="/api")

api_router.include_router(api_v1)
