from sqlmodel import SQLModel, Field
from typing import Optional

class User(SQLModel, table=True):
    # ── FIXED: Clean explicit assignment backed by inline type bypass descriptor ──
    __tablename__ = "users"  # type: ignore
    
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(unique=True)
    password: str # Hashed password pipeline parameter structure
