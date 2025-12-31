from datetime import datetime, timezone, timedelta
import jwt
from pwdlib import PasswordHash
from jwt.exceptions import InvalidTokenError
from app.core.config import settings
from app.schemas.auth import TokenPayload

password_hasher = PasswordHash.recommended()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hasher.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expires_delta

    payload = {
        "sub": subject,
        "exp": expire,
    }
    return jwt.encode(
        payload, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )


def decode_access_token(token: str) -> TokenPayload:
    payload = jwt.decode(
        token, 
        settings.SECRET_KEY, 
        algorithms=[settings.ALGORITHM]
    )

    subject: str = payload.get("sub")
    if subject is None:
        raise InvalidTokenError("Missing subject")
    
    return TokenPayload(
        sub=subject,
        exp=payload.get("exp"),
    )
