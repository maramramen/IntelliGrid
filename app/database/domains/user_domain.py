from datetime import datetime
from pydantic import BaseModel

class User(BaseModel):
    id: int | None = None
    first_name: str
    last_name: str
    username: str
    email_address: str | None = None
    password_hash: str
    is_active: bool = True
    next_login_reset: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None
