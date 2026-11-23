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


class SnapshotUpdate(BaseModel):
    payload: Optional[Dict[str, Any]] = None
    captured_at: Optional[datetime] = None


class SnapshotBatchCreate(BaseModel):
    snapshots: List[SnapshotCreate] = Field(min_length=1, max_length=100)


class SnapshotResponse(BaseModel):
    id: str
    owner_id: str
    captured_at: datetime
    cpu_percent: float
    memory_percent: float
    payload: Dict[str, Any]


class SnapshotOwnerSummary(BaseModel):
    id: str
    owner_email: EmailStr
    captured_at: datetime
    cpu_percent: float
    memory_percent: float


class PaginatedSnapshots(BaseModel):
    items: List[SnapshotResponse]
    page: int
    page_size: int
    total: int


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[str] = Field(default=None, pattern="^(USER|ADMIN)$")


class AlertCreate(BaseModel):
    metric: str = Field(min_length=1, max_length=64)
    threshold: float = Field(ge=0, le=100, allow_inf_nan=False)
    message: str = Field(min_length=1, max_length=512)


class AlertUpdate(BaseModel):
    resolved: bool


class AlertResponse(BaseModel):
    id: str
    owner_id: str
    metric: str
    threshold: float
    message: str
    created_at: datetime
    resolved: bool


class HealthResponse(BaseModel):
    status: str
    database: str
