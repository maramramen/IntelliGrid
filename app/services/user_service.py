import hashlib
from typing import Optional
from passlib.context import CryptContext
from app.database.domains.user_domain import User
from app.database.repositories.user_repository import UserRepository
from app.infrastructure.auth import create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    # ---------------------------
    # Hash de senha seguro
    # ---------------------------
    def _hash_password(self, password: str) -> str:
        sha256_bytes = hashlib.sha256(password.encode()).digest()
        truncated = sha256_bytes[:72]
        return pwd_context.hash(truncated)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        sha256_bytes = hashlib.sha256(plain_password.encode()).digest()
        truncated = sha256_bytes[:72]
        return pwd_context.verify(truncated, hashed_password)

    # ---------------------------
    # Registro de usuário
    # ---------------------------
    def register_user(self, first_name: str, last_name: str, username: str, password: str) -> User:
        hashed = self._hash_password(password)
        user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            password_hash=hashed
        )
        return self.repo.create(user)

    # ---------------------------
    # Login
    # ---------------------------
    def login(self, username: str, password: str) -> Optional[str]:
        user = self.repo.find_by_username(username)
        if user and self._verify_password(password, user.password_hash):
            token = create_access_token({"sub": user.username})
            return token
        return None

    # ---------------------------
    # Atualização de senha
    # ---------------------------
    def update_password(self, username: str, new_password: str) -> bool:
        user = self.repo.find_by_username(username)
        if user:
            self.repo.update_password(user.id, self._hash_password(new_password))
            return True
        return False
