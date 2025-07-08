from typing import Optional, Self, Dict, Any, List
from db.base import MongoManager
from db.managers.customer_managers import CustomerManager
from db.managers.loyalty_action_manager import LoyaltyActionManager
from schemas.config_schemas import ModuleConfig, LoyaltyLevel
from schemas.loyalty_schemas import LoyaltyAction
from dataclasses import dataclass, field
from loguru import logger


@dataclass
class Customer:
    chat_id: int
    config: ModuleConfig
    client_id: str = field(init=False)
    config_id: str = field(init=False)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    balance: int = 0
    level_id: str = "default"
    level: Optional[LoyaltyLevel] = None

    def __post_init__(self):
        self.client_id = self.config.client_id
        self.config_id = self.config.config_id

    @classmethod
    async def load(
        cls, chat_id: int, config: ModuleConfig, session: MongoManager
    ) -> Self:
        customer = cls(chat_id=chat_id, config=config)

        result = await CustomerManager.retrieve(
            db=session,
            chat_id=customer.chat_id,
            client_id=customer.client_id,
            config_id=customer.config_id,
        )

        if not result:
            return customer

        if isinstance(result, dict):
            for attr, value in result.items():
                if hasattr(customer, attr):
                    setattr(customer, attr, value)

        if customer.level_id and config.levels.get(customer.level_id):
            customer.level = config.levels[customer.level_id]

        return customer

    def _dump(self, exclude: dict = {"config"}) -> Dict[str, Any]:
        """Сериализация данных для MongoDB"""
        return {
            name: getattr(self, name)
            for name in self.__annotations__
            if name not in exclude
        }

    async def save(self, session: MongoManager) -> Self:
        try:
            await CustomerManager.update(
                param={
                    "chat_id": self.chat_id,
                    "client_id": self.client_id,
                    "config_id": self.config_id,
                },
                data=self._dump(exclude={"level", "config"}),
                db=session,
            )
            return self
        except Exception as e:
            logger.error(f"Error saving customer: {e}")
            raise

    async def change_balance(
        self, session: MongoManager, amount: int, comment: Optional[str] = None
    ) -> tuple[Self, Optional[str]]:
        try:
            self.balance += amount
            await LoyaltyActionManager.create(
                db=session,
                data=LoyaltyAction(
                    client_id=self.client_id,
                    config_id=self.config_id,
                    chat_id=self.chat_id,
                    amount=amount,
                    comment=comment,
                ).model_dump(),
            )
            await self.save(session=session)
            return self, None
        except Exception as e:
            logger.error(f"Error changing balance: {e}")
            return self, str(e)

    async def change_level(
        self, level: str, session: MongoManager
    ) -> tuple[Self, Optional[str]]:
        try:
            if level not in self.config.levels:
                return self, f"Level '{level}' does not exists"

            self.level_id = level
            self.level = self.config.levels[level]
            await self.save(session=session)
            return self, None
        except Exception as e:
            logger.error(f"Error changing level: {e}")
            return self, str(e)

    async def loyalty_actions(self, session: MongoManager) -> List[LoyaltyAction]:
        try:
            actions = await LoyaltyActionManager.list(
                db=session,
                client_id=self.client_id,
                config_id=self.config_id,
                chat_id=self.chat_id,
            )
            return [LoyaltyAction(**action) for action in actions]
        except Exception as e:
            logger.error(f"Error getting loyalty actions: {e}")
            return []
