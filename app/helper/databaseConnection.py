from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.helpers.config import DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT, DATABASE_NAME

# databaseConntUrl = f"mysql+pymysql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
databaseConntUrl = "postgresql+asyncpg://postgres:Anshujha93#@database-1.cl2g6ws4a3yt.ap-south-1.rds.amazonaws.com/postgres"

engine = create_engine(databaseConntUrl,connect_args={"sslmode": "require"})
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = sessionLocal()
    print("DB connected stabilist")
    try:
        yield db
    finally:
        db.close()