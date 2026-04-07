import uuid
from sqlalchemy import Column, String, Uuid, DateTime
from app.database import Base

class Users(Base):
    __tablename__ = "users"
    username = Column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    email = Column(String, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=False)