"""Prisma client lifecycle and database helpers."""

from collections.abc import AsyncIterator

from prisma import Prisma


db = Prisma()


async def connect_database() -> None:
    """Open the shared Prisma connection."""
    if not db.is_connected():
        await db.connect()


async def disconnect_database() -> None:
    """Close the shared Prisma connection."""
    if db.is_connected():
        await db.disconnect()


async def database_session() -> AsyncIterator[Prisma]:
    """Provide the shared client to route handlers."""
    await connect_database()
    yield db
