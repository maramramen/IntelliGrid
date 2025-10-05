from sys import exception
from app.services.user_service_exception import PasswordUpdateRequiredException, InvalidUsernameOrPasswordException

from fastapi import FastAPI, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.infrastructure.database import SessionLocal, Base, engine
from app.database.models.user import SqlAlchemyUserRepository
from app.services.user_service import UserService
from app.api.schemas.user_schemas import RegisterRequest, LoginRequest, UpdatePasswordRequest

Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/auth")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/adm/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    repo = SqlAlchemyUserRepository(db)
    service = UserService(repo)
    try:
        user = service.register_user(request)
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    return {"msg": "User registered", "user": user.dict(exclude={"password_hash"})}


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    repo = SqlAlchemyUserRepository(db)
    service = UserService(repo)
    try:
        token = service.login(request.username, request.password)
        if not token:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except PasswordUpdateRequiredException as p:
        return {"error_code": p.code, "error_message": str(p)}
    except InvalidUsernameOrPasswordException as i:
        return {"error_code": i.code, "error_message": str(i)}
    return {"access_token": token, "token_type": "bearer"}


@router.post("/update-password")
def update_password(request: UpdatePasswordRequest, db: Session = Depends(get_db)):
    repo = SqlAlchemyUserRepository(db)
    service = UserService(repo)
    try:
        token = service.update_password(request.username, request.current_password, request.new_password)
    except InvalidUsernameOrPasswordException as i:
        return {"error_code": i.code, "error_message": str(i)}
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    return {"access_token": token, "token_type": "bearer"}
