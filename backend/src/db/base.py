import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from loguru import logger
from settings import PROD_DB_NAME


class MongoManager:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

    # database connect and close connections
    async def connect_to_database(self, path: str, user=None, password=None):
        logger.info("Connecting to MongoDB")
        if os.getenv("ENVIROMENT") == "PRODUCTION":
            self.client = AsyncIOMotorClient(
                path,
                username=user,
                password=password,
                # tls=True,
                # tlsCAFile="ca-certificate.crt",
                authSource="admin",
            )
            self.db = self.client[PROD_DB_NAME]
        else:
            self.client = AsyncIOMotorClient(path)
            self.db = self.client.db

        logger.info(
            "Connected to MongoDB -  %s environment!", os.getenv("ENVIROMENT", "DEV")
        )

    async def close_database_connection(self):
        logger.info("Closing connection to MongoDB")
        self.client.close()
        logger.info("MongoDB connection closed")


db = MongoManager()


async def get_database() -> MongoManager:
    return db.db
