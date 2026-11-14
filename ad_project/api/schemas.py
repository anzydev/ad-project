"""Validated API request and response schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class UserLogin(UserCreate):
    pass


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class SnapshotCreate(BaseModel):
    payload: Dict[str, Any]
    captured_at: Optional[datetime] = None


class SnapshotResponse(BaseModel):
    id: str
    owner_id: str
    captured_at: datetime
    cpu_percent: float
    memory_percent: float
    payload: Dict[str, Any]


class PaginatedSnapshots(BaseModel):
    items: List[SnapshotResponse]
    page: int
    page_size: int
    total: int


class HealthResponse(BaseModel):
    status: str
    database: str
