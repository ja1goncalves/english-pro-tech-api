from pydantic import BaseModel
from pymongo.asynchronous.collection import AsyncCollection
from typing import TypeVar, Generic
from app.repository.repository import Repository

T = TypeVar('T')

class Service(Generic[T]):
    def __init__(self, collection: AsyncCollection):
        self.collection = collection
        self.repository = Repository[T](self.collection)

    async def get(self, key: str | dict) -> T | list[T] | None:
        return await self.repository.get(key)

    async def add(self, data: BaseModel) -> T:
        new_data = data.model_dump(by_alias=True, exclude={"id"})
        return await self.repository.add(new_data)

    async def update(self, data) -> T | None:
        return await self.repository.update(data)

    async def remove(self, key: str) -> bool:
        delete_result = await self.repository.remove(key)
        return delete_result.deleted_count == 1

    async def all(self, data_filter = {}, limit = 100, offset = 0) -> list[T]:
        return await self.repository.all(data_filter, limit, offset)