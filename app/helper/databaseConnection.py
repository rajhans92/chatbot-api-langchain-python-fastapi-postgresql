from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.helper.config import (
    DATABASE_USER,
    DATABASE_PASSWORD,
    DATABASE_HOST,
    DATABASE_NAME,
    DATABASE_SSL_MODE
)
from sqlalchemy import text
from urllib.parse import quote_plus
import ssl

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

connect_args = {}

def _database_url(database_name: str) -> str:
    url = (
        "postgresql+asyncpg://"
        f"{quote_plus(DATABASE_USER)}:{quote_plus(DATABASE_PASSWORD)}"
        f"@{DATABASE_HOST}/{quote_plus(database_name)}"
    )
    if DATABASE_SSL_MODE and DATABASE_SSL_MODE.lower() == "true":
        url += "?sslmode=require"
        connect_args["ssl"] = ssl_context
    return url


databaseConntUrl = _database_url(DATABASE_NAME)

engine = create_async_engine(databaseConntUrl, connect_args=connect_args)
sessionLocal = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()


def _quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


async def initialize_database() -> dict:
    """Create the configured database and application tables if missing."""
    if not DATABASE_NAME:
        raise ValueError("DATABASE_NAME is not configured")

    admin_engine = create_async_engine(
        _database_url("postgres"),
        connect_args=connect_args,
        isolation_level="AUTOCOMMIT",
    )
    database_created = False

    try:
        async with admin_engine.connect() as connection:
            result = await connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :database_name"),
                {"database_name": DATABASE_NAME},
            )

            if result.scalar() is None:
                await connection.execute(
                    text(f"CREATE DATABASE {_quote_identifier(DATABASE_NAME)}")
                )
                database_created = True
    finally:
        await admin_engine.dispose()

    async with engine.begin() as connection:
        await connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await connection.run_sync(Base.metadata.create_all)

    return {
        "database": DATABASE_NAME,
        "database_created": database_created,
        "tables_created": True,
    }


async def get_db():
    print("DB connected stabilist")
    try:
        async with sessionLocal() as db:
            yield db
    finally:
        await db.close()