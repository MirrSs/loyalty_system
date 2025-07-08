from http.client import HTTPException
from typing import Any
from fastapi import Depends
from db.base import get_database, MongoManager


class CreateMixin:
    @classmethod
    async def create(cls, db: MongoManager, data: dict):
        await db[cls.tablename].insert_one(data)
        data.pop("_id")
        return data
