from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import settings  # Ambil URL database dari config

# URL database diambil dari .env atau file config
DATABASE_URL = settings.DATABASE_URL

# Membuat engine untuk koneksi ke PostgreSQL dengan asyncpg
engine = create_async_engine(DATABASE_URL, echo=True)

# Session factory untuk AsyncSession
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Dependency untuk mendapatkan session
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
