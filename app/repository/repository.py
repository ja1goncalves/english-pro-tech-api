from bson import ObjectId
from pymongo.asynchronous.collection import AsyncCollection, ReturnDocument
from typing import TypeVar, Generic, Any, Coroutine

from pymongo.results import DeleteResult

T = TypeVar('T')

class Repository(Generic[T]):
    def __init__(self, collection: AsyncCollection):
        self.collection = collection

    async def get(self, key: str | dict) -> T | list[T] | None:
        if type(key) is str:
            return await self.collection.find_one({"_id": ObjectId(key)})
        return list(await self.collection.find(key).to_list(1000))

    async def add(self, data) -> T:
        data = await self.collection.insert_one(data)
        return await self.collection.find_one({"_id": data.inserted_id})

    async def update(self, data) -> T | None:
        return await self.collection.find_one_and_update(
            {"_id": ObjectId(data.id)},
            {"$set": data.model_dump(by_alias=True, exclude={"id"})},
            return_document=ReturnDocument.AFTER
        )

    async def remove(self, key: str) -> DeleteResult:
        return await self.collection.delete_one({"_id": ObjectId(key)})

    async def all(self, data_filter, limit = 100, offset = 0) -> list[T]:
        return list(await self.collection.find(data_filter).skip(offset).limit(limit))