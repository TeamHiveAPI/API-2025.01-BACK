# /home/ubuntu/backend_fastapi_test_files/tests/conftest.py

import pytest
import asyncio
import os
from typing import AsyncGenerator, Generator

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Importe sua aplicação FastAPI e a base do SQLAlchemy (declarative_base)
# Ajuste os caminhos de importação conforme a estrutura do seu projeto
# from main import app # Se main.py está na raiz
# from database import Base, get_async_db # Se database.py está na raiz

# --- Configuração do Banco de Dados de Teste --- 

# Lê a URL do banco de dados das variáveis de ambiente definidas em pytest.ini
# O padrão definido em pytest.ini é SQLite em memória.
TEST_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

print(f"\nUsando banco de dados de teste: {TEST_DATABASE_URL}\n")

# Verifica se está usando SQLite ou PostgreSQL para ajustar connect_args
if TEST_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    connect_args = {}

# Engine assíncrona para testes
async_engine = create_async_engine(TEST_DATABASE_URL, connect_args=connect_args, echo=False)

# Session maker assíncrona para testes
AsyncTestingSessionLocal = async_sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# --- Fixtures do Pytest --- 

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Cria um event loop para o escopo da sessão de teste."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Fixture para criar tabelas do banco de dados de teste uma vez por sessão.
    
    Esta fixture usa a Base do SQLAlchemy importada para criar todas as tabelas
    definidas nos seus modelos (ex: models.py) no banco de dados de teste 
    (SQLite por padrão, ou PostgreSQL se configurado em pytest.ini).
    O usuário 'teste@teste.com' NÃO é criado aqui, ele deve ser criado 
    pela lógica da sua aplicação ao iniciar (se for o caso) ou manualmente 
    no banco de teste se necessário para outros testes.
    """
    # Import Base aqui para garantir que todos os modelos sejam registrados
    # Ajuste o import conforme a estrutura do seu projeto
    from database import Base 
    
    async with async_engine.begin() as conn:
        # Apaga tabelas existentes (cuidado em ambiente não-teste!)
        # await conn.run_sync(Base.metadata.drop_all)
        # Cria todas as tabelas definidas em seus models.py
        await conn.run_sync(Base.metadata.create_all)
    print("\nEstrutura do banco de dados de teste criada.")
    yield
    # Limpeza opcional após todos os testes da sessão
    # async with async_engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)
    # print("\nBanco de dados de teste limpo após a sessão.")

@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Fixture que fornece uma sessão de banco de dados async isolada por teste.
    
    Garante que cada teste receba uma sessão limpa e que as alterações 
    sejam desfeitas (rollback) ao final do teste, evitando interferência.
    """
    async with AsyncTestingSessionLocal() as session:
        yield session
        await session.rollback() # Desfaz quaisquer alterações não commitadas

@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Fixture que cria um cliente de teste HTTPX para interagir com a API.
    
    Sobrescreve a dependência 'get_async_db' da sua aplicação FastAPI 
    para injetar a sessão de banco de dados de teste ('db_session') em vez da 
    sessão de produção. Isso garante que suas rotas usem o banco de teste.
    """
    # Importar app e dependências aqui para garantir que usem o ambiente de teste
    # Ajuste os imports conforme a estrutura do seu projeto
    from main import app
    from database import get_async_db

    # Sobrescrever a dependência get_async_db para usar a sessão de teste
    async def override_get_async_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_async_db] = override_get_async_db

    # Criar o cliente de teste assíncrono
    async with AsyncClient(app=app, base_url="http://testserver") as test_client:
        print("Cliente de teste HTTPX criado.")
        yield test_client

    # Limpar overrides após o teste para não afetar outros contextos
    app.dependency_overrides.clear()

# --- Fixtures para Mocking (Exemplo, se necessário) ---

# @pytest.fixture(autouse=True)
# def mock_send_email(mocker):
#     """Mocka a função de envio de e-mail para todos os testes."""
#     # Ajuste o caminho para sua função de envio de e-mail
#     return mocker.patch("services.email_service.send_email", return_value=True)

# --- Comentários sobre Banco de Dados --- 
# Por padrão, estes testes estão configurados para usar um banco de dados SQLite 
# em arquivo ('./test.db'). Isso é rápido e isolado, ideal para CI e testes locais.
# O schema do banco é criado automaticamente pela fixture 'setup_database' 
# com base nos seus modelos SQLAlchemy (ex: models.py).

# Se você PRECISAR testar especificamente contra PostgreSQL:
# 1. Certifique-se de ter um servidor PostgreSQL rodando para testes.
# 2. Instale o driver async: pip install asyncpg
# 3. No arquivo 'pytest.ini', comente a linha D:DATABASE_URL=sqlite... 
#    e descomente (e ajuste) a linha D:DATABASE_URL=postgresql+asyncpg://...
# 4. Pode ser necessário ajustar a fixture 'setup_database' se a criação/limpeza 
#    do schema precisar de comandos específicos do PostgreSQL ou Alembic.
# Adicione no topo do arquivo
import pytest_asyncio

@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncTestingSessionLocal() as session:
        yield session
        await session.rollback()

@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    from main import app
    from database import get_async_db
    
    # Adicione a configuração do cliente
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_async_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()

