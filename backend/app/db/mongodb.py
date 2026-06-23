from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings


class MongoDB:
    client: AsyncIOMotorClient | None = None
    db: AsyncIOMotorDatabase | None = None

    async def connect(self) -> None:
        self.client = AsyncIOMotorClient(settings.mongodb_uri)
        self.db = self.client[settings.mongodb_db_name]

    async def close(self) -> None:
        if self.client:
            self.client.close()

    def get_db(self) -> AsyncIOMotorDatabase:
        if self.db is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self.db


mongodb = MongoDB()


async def get_db() -> AsyncIOMotorDatabase:
    return mongodb.get_db()
