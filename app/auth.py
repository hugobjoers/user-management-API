import os
import datetime
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
import jwt


class Auth:
    def __init__(self):
        self.PEPPER = os.getenv("PEPPER", "")
        self.SECRET_KEY = os.getenv("SECRET_KEY")
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
        self.pwd_context = CryptContext(schemes=["bcrypt"])
        self.algorithm = "HS256"

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password + self.PEPPER)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password + self.PEPPER, hashed_password)

    def create_access_token(self, data: dict, expires_delta: datetime.timedelta | None = None) -> str:
        """Create an access token. Code taken from https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#hash-and-verify-the-passwords"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
        else:
            expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.algorithm)
        return encoded_jwt


