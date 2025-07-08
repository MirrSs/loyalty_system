from db.managers.crud_manager import CRUDManager


class CustomerManager(CRUDManager):
    tablename = "loyalty_customers"
