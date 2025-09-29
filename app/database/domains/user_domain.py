from datetime import datetime
from pydantic import BaseModel

class User(BaseModel):
    id: int | None = None
    first_name: str
    last_name: str
    username: str
    password_hash: str
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None
