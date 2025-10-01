from pydantic import BaseModel

class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    username: str
    email_address: str | None = None
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class UpdatePasswordRequest(BaseModel):
    username: str
    new_password: str
