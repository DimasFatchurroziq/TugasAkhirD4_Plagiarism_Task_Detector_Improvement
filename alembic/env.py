import os
from logging.config import fileConfig

from sqlalchemy import create_engine
from sqlalchemy import pool

from alembic import context
from src.models.model import Base

target_metadata = Base.metadata
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Fungsi mengambil URL Sync dari file .env Anda
def get_url():
    # Mengambil DATABASE_URL_SYNC, jika tidak ada baru ambil dari alembic.ini
    return os.getenv("DATABASE_URL_SYNC", config.get_main_option("sqlalchemy.url"))

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()  # Menggunakan URL dinamis
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Menggunakan URL dinamis agar membaca konfigurasi kontainer Docker
    connectable = create_engine(
        get_url(),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()