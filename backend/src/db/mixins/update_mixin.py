from typing import Any
from db.base import MongoManager


class UpdateMixin:
    @classmethod
    async def update(cls, param: dict, db: MongoManager, data: dict):
        await db[cls.tablename].update_one(param, {"$set": data})

    @classmethod
    async def update_many(cls, param: dict, db: MongoManager, data: dict):
        await db[cls.tablename].update_many(param, {"$set": data})

