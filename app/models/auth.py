from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class DBUser(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    disabled = Column(Boolean, default=False)