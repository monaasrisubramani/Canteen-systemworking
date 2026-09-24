from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.api.dependencies import get_current_user, get_db
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, LoginResponse, StudentRegisterRequest, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = AuthService(UserRepository(db)).login(data.email, data.password)
    return LoginResponse(access_token=f"demo-user-{user.id}", user=UserResponse(id=user.id, name=user.name, email=user.email, role=user.role))


@router.post("/register", response_model=LoginResponse, status_code=201)
def register_student(data: StudentRegisterRequest, db: Session = Depends(get_db)):
    user = AuthService(UserRepository(db)).register_student(data.name, data.email, data.password)
    return LoginResponse(access_token=f"demo-user-{user.id}", user=UserResponse(id=user.id, name=user.name, email=user.email, role=user.role))

@router.get("/me", response_model=UserResponse)
def get_me(user=Depends(get_current_user)):
    return UserResponse(id=user.id, name=user.name, email=user.email, role=user.role)

@router.post("/logout", status_code=204)
def logout(): pass
