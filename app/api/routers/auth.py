from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.api.deps import get_db
from app.schemas.auth import Token, LoginUser, RegisterUser, UserRead
from app.services.auth import AuthService
from app.domain.exceptions import (
    UsernameAlreadyExistsException,
    UserNotFoundException,
    InvalidCredentialsException,
)
from app.api.deps import get_current_user
from jwt import PyJWTError
from app.core.security import decode_access_token
from app.database.models.user import User
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserRead)
def register(
    payload: RegisterUser,
    db: Session = Depends(get_db),
):
    auth_service = AuthService(db)
    try:
        return auth_service.register(payload.username, payload.password)
    except UsernameAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    auth_service = AuthService(db)
    try:
        access_token = auth_service.login(form_data.username, form_data.password)
        return {"access_token": access_token, "token_type": "bearer"}
    except (UserNotFoundException, InvalidCredentialsException):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user