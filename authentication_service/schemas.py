from pydantic import BaseModel
from typing import Optional, Dict

class UserCreate(BaseModel):
    email: str
    password: str
    role: str
    profile: Optional[Dict] = None

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str