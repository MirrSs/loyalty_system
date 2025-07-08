import asyncio
from loguru import logger
from aiogram import Bot, Dispatcher
from schemas.config_schemas import ModuleConfig
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from settings import TELEGRAM_API_WEBHOOK_URL


class BotManager:
    _instance = None

    def __new__(cls, configs: list[ModuleConfig]):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, configs: list[ModuleConfig]):
        self.configs = configs
        self.bots: dict[str, Bot] = {}
        self.dispatchers: dict[str, Dispatcher] = {}
        self.tasks: list[asyncio.Task] = []  # Для хранения задач ботов

    async def _start_bot(self, config: ModuleConfig):
        """Запуск одного бота"""
        try:
            bot = None
            try:
                bot = Bot(
                    token=config.telegram_token,
                    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
                )
                me = await bot.get_me()  # Test the token is valid
                logger.info(f"Bot @{me.username} is valid")
            except Exception as e:
                logger.error(f"Failed to initialize bot {config.config_id}: {e}")
                return
            dp = Dispatcher()

            # Регистрация обработчиков
            from handlers import start, transport, loyalty, profile

            start.register_handlers(dp, config)
            # order.register_handlers(dp, config)
            loyalty.register_handlers(dp, config)
            profile.register_handlers(dp, config)
            # operator.register_handlers(dp, config)

            # this router have to be last in list, because he handles default text input!
            transport.register_handlers(dp, config)

            self.bots[config.telegram_token] = bot
            self.dispatchers[config.telegram_token] = dp

            await bot.set_webhook(
                url=f"{TELEGRAM_API_WEBHOOK_URL}/{config.client_id}/{config.config_id}",
                allowed_updates=dp.resolve_used_update_types(),
                drop_pending_updates=True,
            )
        except Exception as e:
            logger.error(f"❌ Error while starting bot {config.config_id}: {e}")
            raise

    async def start_all(self):
        """Запуск всех ботов в отдельных задачах"""
        for config in self.configs:
            try:
                task = asyncio.create_task(self._start_bot(config))
                self.tasks.append(task)
                logger.info(f"Starting bot {config.config_id}")
            except Exception as e:
                logger.error(f"Failed to start bot {config.config_id}: {e}")

        # Ждем завершения всех задач (или отмены)
        await asyncio.gather(*self.tasks, return_exceptions=True)

    async def stop_all(self):
        """Остановка всех ботов"""
        for bot in self.bots.values():
            await bot.delete_webhook()
            await bot.session.close()
        for task in self.tasks:
            task.cancel()

    async def stop_bot(self, telegram_token: str) -> bool:
        """Остановка конкретного бота по его токену"""
        if telegram_token not in self.bots:
            return False

        # Отменяем задачу бота
        task_to_cancel = None
        for task in self.tasks:
            if not task.done() and any(
                t == telegram_token for t in self.bots.keys() if t == telegram_token
            ):
                task_to_cancel = task
                break

        if task_to_cancel:
            task_to_cancel.cancel()
            try:
                await task_to_cancel
            except asyncio.CancelledError:
                pass
            self.tasks.remove(task_to_cancel)

        # Закрываем сессию
        await self.bots[telegram_token].delete_webhook()
        await self.bots[telegram_token].session.close()

        # Удаляем из словарей
        del self.bots[telegram_token]
        del self.dispatchers[telegram_token]

        return True

    async def restart_bot(self, config: ModuleConfig) -> bool:
        """
        Перезапускает бота с новой конфигурацией.
        Обновляет конфиг в менеджере, если он уже существует.
        Возвращает True если перезапуск успешен.
        """
        # Обновляем или добавляем конфиг
        config_exists = False
        for i, existing in enumerate(self.configs):
            if existing.config_id == config.config_id:
                self.configs[i] = config
                config_exists = True
                break

        if not config_exists:
            self.configs.append(config)

        # Останавливаем старый экземпляр, если запущен
        if config.telegram_token in self.bots:
            await self.stop_bot(config.telegram_token)

        # Запускаем с новой конфигурацией
        try:
            task = asyncio.create_task(
                self._start_bot(config), name=f"bot_{config.config_id}"
            )
            self.tasks.append(task)
            return True
        except Exception as e:
            logger.error(f"Failed to restart bot {config.config_id}: {e}")
            return False


def get_bot_manager() -> BotManager:
    return BotManager._instance
