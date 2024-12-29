from typing import List, Optional
from bson import ObjectId
from pydantic import BaseModel, Field, field_validator

class AdminResponseDTO(BaseModel):
    id: str = Field(alias="_id")
    username: Optional[str] = None
    domain_name: Optional[str] = None
    status: Optional[str] = None
    feature_list: Optional[List[str]] = []

    @field_validator("id", mode="before")
    def convert_objectid(cls, value):
        if isinstance(value, ObjectId):
            return str(value)
        return value