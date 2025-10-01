from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import Session
from app.infrastructure.database import Base
from app.database.domains.user_domain import User
from app.database.repositories.user_repository import UserRepository

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    email_address = Column(String, unique=False,  nullable=True)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    next_login_reset = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, user: User) -> User:
        db_user = UserModel(**user.dict(exclude={"id"}))
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return User(**db_user.__dict__)

    def find_by_username(self, username: str) -> User | None:
        db_user = self.db.query(UserModel).filter_by(username=username).first()
        return User(**db_user.__dict__) if db_user else None

    def update_password(self, user_id: int, new_password: str) -> None:
        user = self.db.query(UserModel).filter_by(id=user_id).first()
        if user:
            user.password_hash = new_password
            self.db.commit()
