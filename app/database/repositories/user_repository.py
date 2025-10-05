from abc import ABC, abstractmethod
from app.database.domains.user_domain import User


class UserRepository(ABC):
    @abstractmethod
    def create(self, user: User) -> User: ...

    @abstractmethod
    def find_by_username(self, username: str) -> User | None: ...

    @abstractmethod
    def update_password(self, user_id: int, new_password: str) -> User | None: ...
