from typing import Any
from bson.json_util import loads, dumps
from db.base import MongoManager


class ListMixin():
    @classmethod
    async def list(
            cls,
            db: MongoManager,
            **kwargs: Any
    ) :
        obj = db[cls.tablename].find(kwargs)
        obj_list = []
        async for elem in obj:
            elem.pop('_id')
            obj_list.append(loads(dumps(elem)))
        return obj_list