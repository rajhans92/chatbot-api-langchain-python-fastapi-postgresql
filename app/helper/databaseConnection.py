from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import ssl
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# databaseConntUrl = f"mysql+pymysql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
databaseConntUrl = "postgresql+asyncpg://postgres:Anshujha93#@database-1.cl2g6ws4a3yt.ap-south-1.rds.amazonaws.com/postgres?ssl=require"

engine = create_async_engine(databaseConntUrl,connect_args={"ssl": ssl_context})
sessionLocal = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()

async def get_db():
    print("DB connected stabilist")
    try:
        async with sessionLocal() as db:
            yield db
    finally:
        db.close()