from logging.config import fileConfig
import os
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import create_async_engine # <-- Importar create_async_engine
from alembic import context
import asyncio # <-- Importar asyncio

# Alembic Config object
config = context.config

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata para autogenerate
from models import Base
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Executa as migrações no modo offline (sem conexão real)."""
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise Exception("DATABASE_URL not set")

    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection) -> None: # <-- Nova função auxiliar para as migrações
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None: # <-- Agora é uma função async
    """Executa as migrações no modo online (com conexão real)."""
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise Exception("DATABASE_URL not set")

    # Usar create_async_engine
    connectable = create_async_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection: # <-- Conexão async
        await connection.run_sync(do_run_migrations) # <-- Executa as migrações de forma síncrona dentro da conexão assíncrona

# Escolhe o modo conforme o contexto
if context.is_offline_mode():
    run_migrations_offline()
else:
    # Para rodar a função async, precisamos de um loop de eventos
    asyncio.run(run_migrations_online()) # <-- Executa a função async