import datetime
import uuid
import jwt
from typing import Annotated
from pydantic import BaseModel, EmailStr
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from pydantic import BaseModel
from app import models
from app.database import engine, get_db
from app.auth import Auth

models.Base.metadata.create_all(bind=engine)
auth = Auth()
app = FastAPI()

DbSession = Annotated[Session, Depends(get_db)]
class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str

@app.get("/")
def read_root():
    return {"message": "Welcome to Hugo Björs's user management API. Read the documentation at https://github.com/hugobjoers/user-management-API for additional context."}

@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: DbSession):
    """Create a user given an email and password"""
    user = models.Users(
        email=user.email,
        hashed_password=auth.hash_password(user.password),
        last_login=datetime.datetime.now(datetime.timezone.utc),
    )
    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists or data violates a constraint",
            )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while creating user",
        )

    db.refresh(user)
    return {
        "message": "User created",
        "username": str(user.username),
    }

@app.post("/login", status_code=status.HTTP_200_OK)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession):
    """Login using a username and password. A message and a JWT token is returned."""
    failed_login = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID or password",
            )

    stmt = select(models.Users).where(models.Users.username == form_data.username)
    user = db.scalar(stmt)
    
    if user is None:
        #We know that it's because it was an invalid username. This is not stated to help mitigate brute force attacks.
        raise failed_login 

    login_success = auth.verify_password(form_data.password, user.hashed_password)
    if not login_success:
        raise failed_login
    
    stmt = update(models.Users).where(models.Users.username == form_data.username).values(last_login=datetime.datetime.now(datetime.timezone.utc))
    db.execute(stmt)
    db.commit()

    access_token = auth.create_access_token(
        data={"sub": str(user.username)}, expires_delta=datetime.timedelta(minutes=30)
    )
    
    return {
        "message": "Login successful",
        "token": Token(access_token=access_token, token_type="bearer")
    }
    
@app.get("/users/self", status_code=status.HTTP_200_OK)
def get_current_user(token: Annotated[str, Depends(auth.oauth2_scheme)], db: DbSession):
    """Return the currently logged in user. A JWT token is required for authentication."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.algorithm])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        username = uuid.UUID(username)
    except (jwt.InvalidTokenError, ValueError):
        raise credentials_exception                                                                                                         

    user = db.scalar(select(models.Users).where(models.Users.username == username))
    if user is None:
        raise credentials_exception
    
    return user #Hashed password should not be returned in real world usage. This is mostly to show that the password is indeed hashed.