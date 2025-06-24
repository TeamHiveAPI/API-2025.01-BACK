import pytest
import asyncio
import os
from typing import AsyncGenerator

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Importe suas dependências (ajuste os caminhos)
from main import app
from database import Base, get_async_db

# --- Configuração do Banco de Dados ---
TEST_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

print(f"\n🔧 Usando banco de dados de teste: {TEST_DATABASE_URL}\n")

# Configuração da engine (suporta SQLite e PostgreSQL)
connect_args = {}
if TEST_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

async_engine = create_async_engine(TEST_DATABASE_URL, connect_args=connect_args, echo=False)
AsyncTestingSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)

# --- Fixtures Principais ---
@pytest.fixture(scope="session")
def event_loop():
    """Cria um event loop para testes assíncronos."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Cria as tabelas no banco de testes."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("\n✅ Tabelas do banco de dados criadas.")
    yield
    # (Opcional) Descomente para limpar o banco após os testes:
    # async with async_engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Fornece uma sessão isolada por teste."""
    async with AsyncTestingSessionLocal() as session:
        yield session
        await session.rollback()  # Rollback para não persistir dados entre testes

@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Cliente HTTPX para testar a API FastAPI."""
    # Sobrescreve a dependência do banco de dados
    app.dependency_overrides[get_async_db] = lambda: db_session
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()  # Limpa overrides após o teste