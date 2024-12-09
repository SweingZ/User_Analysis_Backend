from typing import List, Optional
from pydantic import BaseModel, Field

class Admin(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    domain_name: Optional[str] = None
    users_list: Optional[List[str]] = []
    status: Optional[str] = Field(default="PENDING")
    role: Optional[str] = Field(default="ADMIN")
