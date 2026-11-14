"""Versioned backend API routes."""

import json
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from prisma import Prisma

from ad_project.api.config import Settings, get_settings
from ad_project.api.database import database_session
from ad_project.api.dependencies import get_current_user, require_admin
from ad_project.api.schemas import (
    HealthResponse,
    PaginatedSnapshots,
    SnapshotCreate,
    SnapshotResponse,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from ad_project.api.security import create_access_token, hash_password, verify_password
from ad_project.api.serialization import persisted_snapshot_response, snapshot_record
from ad_project.collectors import SystemMonitor


router = APIRouter(prefix="/api/v1")
auth_router = APIRouter(prefix="/auth", tags=["authentication"])
snapshot_router = APIRouter(prefix="/snapshots", tags=["snapshots"])
admin_router = APIRouter(prefix="/admin", tags=["administration"])


def user_response(user) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        created_at=user.created_at,
    )


@router.get("/health", response_model=HealthResponse, tags=["system"])
async def health(db: Prisma = Depends(database_session)) -> HealthResponse:
    """Report API and database availability."""
    try:
        await db.query_raw("SELECT 1")
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    return HealthResponse(status="ok", database="ok")


@auth_router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: UserCreate,
    db: Prisma = Depends(database_session),
    settings: Settings = Depends(get_settings),
) -> TokenResponse:
    """Create a user account and return a short-lived access token."""
    email = str(request.email).lower()
    existing = await db.user.find_unique(where={"email": email})
    if existing is not None:
        raise HTTPException(status_code=409, detail="Email is already registered")
    user = await db.user.create(
        data={"email": email, "password_hash": hash_password(request.password)}
    )
    return TokenResponse(
        access_token=create_access_token(user.id, user.role, settings),
        user=user_response(user),
    )


@auth_router.post("/login", response_model=TokenResponse)
async def login(
    request: UserLogin,
    db: Prisma = Depends(database_session),
    settings: Settings = Depends(get_settings),
) -> TokenResponse:
    """Authenticate a user without revealing whether an email exists."""
    user = await db.user.find_unique(where={"email": str(request.email).lower()})
    if user is None or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return TokenResponse(
        access_token=create_access_token(user.id, user.role, settings),
        user=user_response(user),
    )


@auth_router.get("/me", response_model=UserResponse)
async def me(current_user=Depends(get_current_user)) -> UserResponse:
    """Return the authenticated user."""
    return user_response(current_user)


@snapshot_router.post("", response_model=SnapshotResponse, status_code=status.HTTP_201_CREATED)
async def create_snapshot(
    request: SnapshotCreate,
    db: Prisma = Depends(database_session),
    current_user=Depends(get_current_user),
) -> SnapshotResponse:
    """Persist a client-provided monitor snapshot owned by the caller."""
    cpu = request.payload.get("cpu", {}).get("overall_percent", 0)
    memory = request.payload.get("memory", {}).get("ram_percent", 0)
    try:
        cpu_percent = float(cpu)
        memory_percent = float(memory)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail="Snapshot CPU and memory values must be numeric") from exc
    data = {
        "owner_id": current_user.id,
        "cpu_percent": cpu_percent,
        "memory_percent": memory_percent,
        "payload": json.dumps(request.payload, default=str),
    }
    if request.captured_at is not None:
        data["captured_at"] = request.captured_at
    record = await db.snapshot.create(data=data)
    return SnapshotResponse(**persisted_snapshot_response(record))


@snapshot_router.post("/collect", response_model=SnapshotResponse, status_code=status.HTTP_201_CREATED)
async def collect_snapshot(
    db: Prisma = Depends(database_session),
    current_user=Depends(get_current_user),
) -> SnapshotResponse:
    """Collect the current local system metrics and persist them for the caller."""
    snapshot = SystemMonitor().collect_snapshot()
    record = await db.snapshot.create(data=snapshot_record(snapshot, current_user.id))
    return SnapshotResponse(**persisted_snapshot_response(record))


@snapshot_router.get("", response_model=PaginatedSnapshots)
async def list_snapshots(
    db: Prisma = Depends(database_session),
    current_user=Depends(get_current_user),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sort: str = Query(default="captured_at", pattern="^(captured_at|cpu_percent|memory_percent)$"),
    order: str = Query(default="desc", pattern="^(asc|desc)$"),
    from_time: Optional[datetime] = None,
    to_time: Optional[datetime] = None,
) -> PaginatedSnapshots:
    """List only the caller's snapshots with bounded pagination and sorting."""
    where = {"owner_id": current_user.id}
    if from_time or to_time:
        where["captured_at"] = {}
        if from_time:
            where["captured_at"]["gte"] = from_time
        if to_time:
            where["captured_at"]["lte"] = to_time
    total = await db.snapshot.count(where=where)
    records = await db.snapshot.find_many(
        where=where,
        skip=(page - 1) * page_size,
        take=page_size,
        order={"captured_at": order} if sort == "captured_at" else {sort: order},
    )
    return PaginatedSnapshots(
        items=[SnapshotResponse(**persisted_snapshot_response(record)) for record in records],
        page=page,
        page_size=page_size,
        total=total,
    )


@admin_router.get("/users", response_model=List[UserResponse])
async def list_users(
    db: Prisma = Depends(database_session),
    current_user=Depends(get_current_user),
) -> List[UserResponse]:
    """List users for administrators, demonstrating centralized role enforcement."""
    require_admin(current_user)
    users = await db.user.find_many(order={"created_at": "desc"}, take=100)
    return [user_response(user) for user in users]


router.include_router(auth_router)
router.include_router(snapshot_router)
router.include_router(admin_router)
