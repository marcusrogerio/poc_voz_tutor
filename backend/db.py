# db.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from config import POSTGRES_URL

if not POSTGRES_URL:
    raise RuntimeError("POSTGRES_URL não está definido no .env")

engine = create_async_engine(
    POSTGRES_URL,
    echo=True,          # pode deixar True por enquanto para debugar
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

Base = declarative_base()
