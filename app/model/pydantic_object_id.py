from typing import Annotated, Any, Callable
from bson import ObjectId
from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema


class _ObjectIdPydanticAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
            cls, source_type: Any, handler: Callable[[Any], core_schema.CoreSchema]
    ) -> core_schema.CoreSchema:
        return core_schema.union_schema(
            [
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema(
                    [
                        core_schema.str_schema(),
                        core_schema.no_info_plain_validator_function(cls.validate),
                    ]
                ),
            ],
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def __get_pydantic_json_schema__(
            cls, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return handler(core_schema)

    @classmethod
    def validate(cls, value: str) -> ObjectId:
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")
        return ObjectId(value)


PydanticObjectId = Annotated[ObjectId, _ObjectIdPydanticAnnotation]
