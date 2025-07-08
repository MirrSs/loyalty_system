from db.mixins.retrieve_mixin import RetrieveMixin
from db.mixins.list_mixin import ListMixin
from db.mixins.create_mixin import CreateMixin
from db.mixins.delete_mixin import DeleteMixin
from db.mixins.update_mixin import UpdateMixin

class CRUDManager(
    ListMixin,
    RetrieveMixin,
    CreateMixin,
    UpdateMixin,
    DeleteMixin
):
    pass
