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

    async def update(self, data) -> bool:
        update_result = await self.repository.update(data)
        return update_result is not None

    async def remove(self, key: str) -> bool:
        delete_result = await self.repository.remove(key)
        return delete_result is not None

    async def all(self, data_filter = {}, limit = 100, offset = 0) -> list[T]:
        return await self.repository.all(data_filter, limit, offset)

    async def filtering(self, params: dict) -> list[dict]:
        limit = params["limit"] if "limit" in params else 100
        offset = params["offset"] if "offset" in params else 0
        filter_params = {k: v for k, v in params.items() if k not in ["limit", "offset"] and v not in [None, '']}
        return await self.all(filter_params, limit, offset)