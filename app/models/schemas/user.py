from pydantic import BaseModel
from datetime import datetime

class UserBase(BaseModel):
    """Base schema with common attributes"""
    email: str

class UserCreate(UserBase):
    """Properties to receive on user creation"""
    id: str 

class UserOut(UserBase):
    """Properties to return to client"""
    id: str
    created_at: datetime

    class Config:
        from_attributes = True # Enable ORM mode