import hashlib
from logging import exception

from app.services.user_service_exception import PasswordUpdateRequiredException, InvalidUsernameOrPasswordException
from typing import Optional
from passlib.context import CryptContext
import re

from passlib.crypto.scrypt import validate

from app.api.schemas.user_schemas import RegisterRequest
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
        sha256_hex = hashlib.sha256(password.encode()).hexdigest()
        return pwd_context.hash(sha256_hex)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        sha256_hex = hashlib.sha256(plain_password.encode()).hexdigest()
        return pwd_context.verify(sha256_hex, hashed_password)

    # ---------------------------
    # Register user
    # ---------------------------
    def register_user(self, dto: RegisterRequest) -> User:
        if (
                dto is None
                or dto.password in ["", None]
                or dto.username in ["", None]
                or dto.first_name in ["", None]
                or dto.last_name in ["", None]
        ):
            raise ValueError("All fields are required")
        if not self.validate_password(dto.password):
            raise ValueError("""Password should contain at least 8 characters, an uppercase letter, lowercase letter, a number a special character (!@#$%^&* etc.)""")
        try:
            existing_username = self.repo.find_by_username(dto.username)
            if existing_username is not None:
                raise ValueError("Username already exists")
            hashed = self._hash_password(dto.password)
            user = User(
                first_name=dto.first_name,
                last_name=dto.last_name,
                username=dto.username,
                email_address=dto.email_address,
                password_hash=hashed
            )
            return self.repo.create(user)
        except Exception as e:
            raise ValueError(str(e))


    # ---------------------------
    # Login
    # ---------------------------
    def login(self, username: str, password: str, is_update: bool = False) -> Optional[str]:
        user = self.repo.find_by_username(username)
        if not is_update and user.next_login_reset:
            raise PasswordUpdateRequiredException("Password update required", code=1001)
        if user and self._verify_password(password, user.password_hash):
            token = create_access_token({"sub": user.username})
            return token
        raise InvalidUsernameOrPasswordException("Invalid username or password", code=1002)

    # ---------------------------
    # Updates password
    # ---------------------------
    def update_password(self, username: str, current_password: str, new_password: str) -> Optional[str]:
        if not self.validate_password(new_password):
            raise ValueError(
                """New password should contain at least 8 characters, an uppercase letter, lowercase letter, a number a special character (!@#$%^&* etc.)""")
        user = self.repo.find_by_username(username)
        if user and self._verify_password(current_password, user.password_hash):
            user = self.repo.update_password(user.id, self._hash_password(new_password))
            if user and self._verify_password(new_password, user.password_hash):
                token = create_access_token({"sub": user.username})
                return token
        raise InvalidUsernameOrPasswordException("Invalid username or password", code=1002)

    # ---------------------------
    # Password validation
    # ---------------------------
    def validate_password(self, password: str) -> bool:
        """
        Validates if the password is secure:
        - At least 8 characters
        - Contains an uppercase letter
        - Contains a lowercase letter
        - Contains a number
        - Contains a special character (!@#$%^&* etc.)
        """
        if len(password) < 8:
            return False

        if not re.search(r"[A-Z]", password):  # Contains an uppercase letter
            return False

        if not re.search(r"[a-z]", password):  # Contains a lowercase letter
            return False

        if not re.search(r"[0-9]", password):  # Contains a number
            return False

        if not re.search(r"[\W_]", password):  # Contains a special character (!@#$%^&* etc.)
            return False

        return True
