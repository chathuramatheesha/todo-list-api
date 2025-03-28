from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.hash import bcrypt
from jose import jwt
from datetime import datetime, timedelta, timezone

from app.config import config


class Hash:
    @staticmethod
    def get_hash_password(password: str) -> str:
        return bcrypt.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.verify(plain_password, hashed_password)


oath2_scheme = OAuth2PasswordBearer(tokenUrl="token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def access_token_expire_minutes() -> int:
    return config.ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=access_token_expire_minutes()
    )

    jwt_data = {"sub": email, "exp": expire}
    encoded_jwt = jwt.encode(
        jwt_data,
        key=config.SECRET_KEY,
        algorithm=config.ALGORITHM,
    )

    return encoded_jwt
