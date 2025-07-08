from http.client import HTTPException
from typing import Any
from fastapi import Depends
from db.base import get_database, MongoManager


class RetrieveMixin():
    @classmethod
    async def retrieve(
            cls,
            db: MongoManager,
            **kwargs: Any
    ) :
        obj = db[cls.tablename].find(kwargs)
        async for elem in obj:
            elem.pop('_id')
            return elem