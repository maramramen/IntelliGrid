from fastapi import FastAPI, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from app.infrastructure.database import SessionLocal, Base, engine
from app.database.models.user import SqlAlchemyUserRepository
from app.services.user_service import UserService
from app.api.schemas.user_schemas import RegisterRequest, LoginRequest, UpdatePasswordRequest

Base.metadata.create_all(bind=engine)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    repo = SqlAlchemyUserRepository(db)
    service = UserService(repo)
    user = service.register_user(
        request.first_name,
        request.last_name,
        request.username,
        request.password
    )
    return {"msg": "User registered", "user": user.dict(exclude={"password_hash"})}


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    repo = SqlAlchemyUserRepository(db)
    service = UserService(repo)
    token = service.login(request.username, request.password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": token, "token_type": "bearer"}


@router.post("/update-password")
def update_password(request: UpdatePasswordRequest, db: Session = Depends(get_db)):
    repo = SqlAlchemyUserRepository(db)
    service = UserService(repo)
    success = service.update_password(request.username, request.new_password)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"msg": "Password updated"}
