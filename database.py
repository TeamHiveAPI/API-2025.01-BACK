from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# URL de conexão assíncrona com o PostgreSQL
DATABASE_URL = "postgresql+asyncpg://postgres:1234@localhost:5432/api"

# Criar a engine assíncrona
async_engine = create_async_engine(DATABASE_URL, echo=True)

# Configurar a sessão assíncrona
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base para os modelos
Base = declarative_base()

# Função para criar as tabelas de forma assíncrona
async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Função para gerenciar a sessão assíncrona do banco
async def get_async_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()