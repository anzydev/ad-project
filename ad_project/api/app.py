"""FastAPI application entrypoint for the AD-Project backend."""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from ad_project.api.background import collect_periodically
from ad_project.api.config import get_settings
from ad_project.api.database import connect_database, db, disconnect_database
from ad_project.api.routes import router
from ad_project.api.security import hash_password
from ad_project.api.middleware import LoginRateLimitMiddleware

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    await connect_database()
    collection_task = None
    if settings.admin_email and settings.admin_password:
        admin = await db.user.find_unique(where={"email": settings.admin_email.lower()})
        if admin is None:
            await db.user.create(
                data={
                    "email": settings.admin_email.lower(),
                    "password_hash": hash_password(settings.admin_password),
                    "role": "ADMIN",
                }
            )
    if settings.enable_background_collection and settings.admin_email:
        owner = await db.user.find_unique(where={"email": settings.admin_email.lower()})
        if owner is not None:
            collection_task = asyncio.create_task(
                collect_periodically(db, settings, owner.id)
            )
    try:
        yield
    finally:
        if collection_task is not None:
            collection_task.cancel()
            await asyncio.gather(collection_task, return_exceptions=True)
        await disconnect_database()


app = FastAPI(
    title="AD-Project Monitor API",
    version="1.0.0",
    description="Authenticated API and PostgreSQL persistence for the AD-Project terminal monitor.",
    lifespan=lifespan,
)
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.api_allowed_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)
app.add_middleware(LoginRateLimitMiddleware, settings=settings)


@app.middleware("http")
async def enforce_transport(request: Request, call_next):
    """Require HTTPS when deployed behind a TLS-terminating proxy."""
    if settings.require_https and request.headers.get("x-forwarded-proto", request.url.scheme) != "https":
        return JSONResponse(
            status_code=400,
            content={"error": {"code": "https_required", "message": "HTTPS is required"}},
        )
    return await call_next(request)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """Return one safe response shape for invalid external input."""
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "Request validation failed",
                "details": exc.errors(),
            }
        },
    )


@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception):
    """Avoid leaking internal details while retaining server-side diagnostics."""
    logging.getLogger(__name__).exception("Unhandled API error")
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "internal_error", "message": "Internal server error"}},
    )


app.include_router(router)


def run() -> None:
    """Run the API server from the installed ``ad-api`` command."""
    uvicorn.run("ad_project.api.app:app", host="127.0.0.1", port=8000)
