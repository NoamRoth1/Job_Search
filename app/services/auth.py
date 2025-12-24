from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.schemas.user import TokenData

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def create_user(self, email: str, password: str) -> User:
        hashed_password = self.hash_password(password)
        user = User(email=email, hashed_password=hashed_password, created_at=datetime.utcnow())
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = self.get_user_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or settings.access_token_expires())
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    def decode_token(self, token: str) -> Optional[TokenData]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email: str | None = payload.get("sub")
            if email is None:
                return None
            return TokenData(email=email)
        except JWTError:
            return None
