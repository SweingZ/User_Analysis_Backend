from pydantic import BaseModel, Field, field_validator
from bson import ObjectId
from typing import Optional

class UserResponseDTO(BaseModel):
    id: str = Field(alias="_id")
    username: Optional[str] = None
    session_count: Optional[int] = None

    @field_validator("id", mode="before")
    def convert_objectid(cls, value):
        if isinstance(value, ObjectId):
            return str(value)
        return value
