"""Versioned backend API routes."""

import json
import math
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from prisma import Prisma
from prisma.errors import UniqueViolationError
from starlette.concurrency import run_in_threadpool

from ad_project.api.config import Settings, get_settings
from ad_project.api.database import database_session
from ad_project.api.dependencies import get_current_user, require_admin
from ad_project.api.schemas import (
    AlertCreate,
    AlertResponse,
    AlertUpdate,
    HealthResponse,
    PaginatedSnapshots,
    SnapshotCreate,
    SnapshotResponse,
    SnapshotOwnerSummary,
    SnapshotUpdate,
    SnapshotBatchCreate,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)
from ad_project.api.security import create_access_token, hash_password, verify_password
from ad_project.api.serialization import persisted_snapshot_response, snapshot_record
from ad_project.collectors import SystemMonitor


router = APIRouter(prefix="/api/v1")
auth_router = APIRouter(prefix="/auth", tags=["authentication"])
snapshot_router = APIRouter(prefix="/snapshots", tags=["snapshots"])
alert_router = APIRouter(prefix="/alerts", tags=["alerts"])
admin_router = APIRouter(prefix="/admin", tags=["administration"])


def user_response(user) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        created_at=user.created_at,
    )


def snapshot_metrics(payload: dict) -> tuple[float, float]:
    """Validate the values stored in both scalar columns and the JSON payload."""
    try:
        cpu = float(payload["cpu"]["overall_percent"])
        memory = float(payload["memory"]["ram_percent"])
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        raise HTTPException(
            status_code=422,
            detail="Payload requires numeric cpu.overall_percent and memory.ram_percent",
        ) from exc
    if not (math.isfinite(cpu) and math.isfinite(memory) and 0 <= cpu <= 100 and 0 <= memory <= 100):
        raise HTTPException(
            status_code=422, detail="Snapshot CPU and memory values must be between 0 and 100"
        )
    return cpu, memory


def alert_response(alert) -> AlertResponse:
    return AlertResponse(
        id=alert.id, owner_id=alert.owner_id, metric=alert.metric,
        threshold=alert.threshold, message=alert.message,
        created_at=alert.created_at, resolved=alert.resolved,
    )


@router.get("/health", response_model=HealthResponse, tags=["system"])
async def health(db: Prisma = Depends(database_session)) -> HealthResponse:
    """Report API and database availability."""
    try:
        await db.query_raw("SELECT 1")
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    return HealthResponse(status="ok", database="ok")


@router.get("/metrics/live", tags=["system"])
async def get_live_metrics() -> dict:
    """Live system telemetry snapshot for real-time 3D and VR visualization."""
    from ad_project.exporter import snapshot_to_dict
    snapshot = await run_in_threadpool(SystemMonitor().collect_snapshot)
    return snapshot_to_dict(snapshot)


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
    try:
        user = await db.user.create(
            data={"email": email, "password_hash": await run_in_threadpool(hash_password, request.password)}
        )
    except UniqueViolationError as exc:
        raise HTTPException(status_code=409, detail="Email is already registered") from exc
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
    if user is None or not await run_in_threadpool(verify_password, request.password, user.password_hash):
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
    cpu_percent, memory_percent = snapshot_metrics(request.payload)
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
    snapshot = await run_in_threadpool(SystemMonitor().collect_snapshot)
    record = await db.snapshot.create(data=snapshot_record(snapshot, current_user.id))
    return SnapshotResponse(**persisted_snapshot_response(record))


@snapshot_router.post("/batch", response_model=List[SnapshotResponse], status_code=status.HTTP_201_CREATED)
async def create_snapshot_batch(
    request: SnapshotBatchCreate,
    db: Prisma = Depends(database_session),
    current_user=Depends(get_current_user),
) -> List[SnapshotResponse]:
    """Create multiple snapshots atomically; any failure rolls back the batch."""
    records = []
    async with db.tx() as transaction:
        for item in request.snapshots:
            cpu_percent, memory_percent = snapshot_metrics(item.payload)
            data = {
                "owner_id": current_user.id,
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "payload": json.dumps(item.payload, default=str),
            }
            if item.captured_at is not None:
                data["captured_at"] = item.captured_at
            records.append(await transaction.snapshot.create(data=data))
    return [SnapshotResponse(**persisted_snapshot_response(record)) for record in records]


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


@snapshot_router.get("/{snapshot_id}/summary", response_model=SnapshotOwnerSummary)
async def get_snapshot_owner_summary(
    snapshot_id: str,
    db: Prisma = Depends(database_session),
    current_user=Depends(get_current_user),
) -> SnapshotOwnerSummary:
    """One parameterized JOIN, selecting only the owner and reading metrics.

    Avoid fetching the large serialized payload or one User query per snapshot.
    """
    rows = await db.query_raw(
        'SELECT s."id", u."email" AS "owner_email", s."captured_at", '
        's."cpu_percent", s."memory_percent" '
        'FROM "Snapshot" AS s '
        'JOIN "User" AS u ON u."id" = s."owner_id" '
        'WHERE s."id" = $1 AND s."owner_id" = $2 LIMIT 1',
        snapshot_id,
        current_user.id,
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    return SnapshotOwnerSummary(**rows[0])


@snapshot_router.patch("/{snapshot_id}", response_model=SnapshotResponse)
async def update_snapshot(
    snapshot_id: str,
    request: SnapshotUpdate,
    db: Prisma = Depends(database_session),
    current_user=Depends(get_current_user),
) -> SnapshotResponse:
    """Update a snapshot owned by the authenticated caller."""
    record = await db.snapshot.find_first(
        where={"id": snapshot_id, "owner_id": current_user.id}
    )
    if record is None:
        raise HTTPException(status_code=404, detail="Snapshot not found")

    data = {}
    if request.payload is not None:
        cpu_percent, memory_percent = snapshot_metrics(request.payload)
        data.update({
            "payload": json.dumps(request.payload, default=str),
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
        })
    if request.captured_at is not None:
        data["captured_at"] = request.captured_at

    if not data:
        return SnapshotResponse(**persisted_snapshot_response(record))

    record = await db.snapshot.update(where={"id": snapshot_id}, data=data)
    return SnapshotResponse(**persisted_snapshot_response(record))


@snapshot_router.delete("/{snapshot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_snapshot(
    snapshot_id: str,
    db: Prisma = Depends(database_session),
    current_user=Depends(get_current_user),
) -> None:
    """Delete a snapshot owned by the authenticated caller."""
    record = await db.snapshot.find_first(
        where={"id": snapshot_id, "owner_id": current_user.id}
    )
    if record is None:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    await db.snapshot.delete(where={"id": snapshot_id})


@admin_router.get("/users", response_model=List[UserResponse])
async def list_users(
    db: Prisma = Depends(database_session),
    current_user=Depends(get_current_user),
) -> List[UserResponse]:
    """List users for administrators, demonstrating centralized role enforcement."""
    require_admin(current_user)
    users = await db.user.find_many(order={"created_at": "desc"}, take=100)
    return [user_response(user) for user in users]


@admin_router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    request: UserUpdate,
    db: Prisma = Depends(database_session),
    current_user=Depends(get_current_user),
) -> UserResponse:
    """Update a user for administrators only."""
    require_admin(current_user)
    existing = await db.user.find_unique(where={"id": user_id})
    if existing is None:
        raise HTTPException(status_code=404, detail="User not found")

    data = {}
    if request.email is not None:
        data["email"] = str(request.email).lower()
    if request.role is not None:
        data["role"] = request.role
    if not data:
        return user_response(existing)

    try:
        updated = await db.user.update(where={"id": user_id}, data=data)
    except UniqueViolationError as exc:
        raise HTTPException(status_code=409, detail="Email is already in use") from exc
    return user_response(updated)


@admin_router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    db: Prisma = Depends(database_session),
    current_user=Depends(get_current_user),
) -> None:
    """Delete a user and owned records for administrators only."""
    require_admin(current_user)
    if user_id == current_user.id:
        raise HTTPException(status_code=409, detail="Administrators cannot delete themselves")
    existing = await db.user.find_unique(where={"id": user_id})
    if existing is None:
        raise HTTPException(status_code=404, detail="User not found")
    await db.user.delete(where={"id": user_id})


@alert_router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    request: AlertCreate,
    db: Prisma = Depends(database_session),
    current_user=Depends(get_current_user),
) -> AlertResponse:
    """Save a monitoring alert owned by the authenticated caller."""
    record = await db.alert.create(data={
        "owner_id": current_user.id, "metric": request.metric,
        "threshold": request.threshold, "message": request.message,
    })
    return alert_response(record)


@alert_router.get("", response_model=List[AlertResponse])
async def list_alerts(
    resolved: Optional[bool] = None,
    limit: int = Query(default=50, ge=1, le=100),
    db: Prisma = Depends(database_session),
    current_user=Depends(get_current_user),
) -> List[AlertResponse]:
    """List the caller's alerts with bounded results."""
    where = {"owner_id": current_user.id}
    if resolved is not None:
        where["resolved"] = resolved
    records = await db.alert.find_many(
        where=where, take=limit, order={"created_at": "desc"}
    )
    return [alert_response(record) for record in records]


@alert_router.patch("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: str,
    request: AlertUpdate,
    db: Prisma = Depends(database_session),
    current_user=Depends(get_current_user),
) -> AlertResponse:
    """Mark an owned alert resolved or unresolved."""
    record = await db.alert.find_first(where={
        "id": alert_id, "owner_id": current_user.id,
    })
    if record is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    updated = await db.alert.update(
        where={"id": alert_id}, data={"resolved": request.resolved}
    )
    return alert_response(updated)


@alert_router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: str,
    db: Prisma = Depends(database_session),
    current_user=Depends(get_current_user),
) -> None:
    """Remove an alert owned by the authenticated caller."""
    record = await db.alert.find_first(where={
        "id": alert_id, "owner_id": current_user.id,
    })
    if record is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    await db.alert.delete(where={"id": alert_id})


router.include_router(auth_router)
router.include_router(snapshot_router)
router.include_router(alert_router)
router.include_router(admin_router)
