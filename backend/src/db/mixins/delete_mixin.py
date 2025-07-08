from http.client import HTTPException
from typing import Any
from fastapi import Depends
from db.base import get_database, MongoManager


class DeleteMixin:
    @classmethod
    async def delete(
        cls,
        db: MongoManager,
        **kwargs: Any
    ):
        return await db[cls.tablename].delete_one(kwargs)
