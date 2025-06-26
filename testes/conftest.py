import pytest
import pytest_asyncio
import asyncio
import sys
import os
from typing import AsyncGenerator

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Ajusta path para importar módulos do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Importa seu app e banco
from main import app
from database import Base, get_async_db

# Usa variável de ambiente DATABASE_URL ou padrão sqlite para testes
TEST_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

print(f"\n🔧 Usando banco de dados de teste: {TEST_DATABASE_URL}\n")

# Configura argumentos da engine para SQLite e PostgreSQL
connect_args = {}
if TEST_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Cria engine async para o banco de testes
async_engine = create_async_engine(TEST_DATABASE_URL, connect_args=connect_args, echo=False)
AsyncTestingSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)

# Fixture para o event loop (escopo session)
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Fixture para criar e dropar tabelas (escopo session e autouse para rodar sempre)
@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    # Cria tabelas
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("\n✅ Tabelas criadas no banco de testes.")
    yield
    # Opcional: dropa as tabelas depois dos testes (descomente se quiser)
    # async with async_engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)

# Fixture para criar uma sessão de banco isolada para cada teste
@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncTestingSessionLocal() as session:
        yield session
        # Faz rollback para não persistir alterações entre testes
        await session.rollback()

# Fixture para cliente HTTPX com FastAPI, injetando o db_session na dependência do app
@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    # Override da dependência de banco de dados
    app.dependency_overrides[get_async_db] = lambda: db_session
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client
    # Limpa overrides após o teste para não afetar outros testes
    app.dependency_overrides.clear()
