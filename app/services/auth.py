from sqlmodel import Session, select
from app.database.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from app.domain.exceptions import (
    UsernameAlreadyExistsException,
    UserNotFoundException,
    InvalidCredentialsException,
)

class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    def register(self, username: str, password: str) -> User | None:
        existing_user = self.db.exec(
            select(User).where(User.username == username)
        ).first()

        if existing_user:
            raise UsernameAlreadyExistsException()

        password_hash = hash_password(password)

        user = User(
            username=username,
            password_hash=password_hash,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def authenticate(self, username: str, password: str) -> User | None:
        user = self.db.exec(
            select(User).where(User.username == username)
        ).first()

        if not user:
            raise UserNotFoundException()

        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsException()

        return user

    def login(self, username: str, password: str) -> str | None:
        user = self.authenticate(username, password)
        return create_access_token(subject=user.username)
