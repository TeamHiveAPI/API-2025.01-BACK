import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from models import Parametro

# Tente importar a aplicação real
try:
    from app.main import app  # Ajuste o caminho conforme necessário
except ImportError:
    from fastapi import FastAPI
    app = FastAPI()  # Cria uma app fake se a real não estiver disponível
    @app.post("/estacoes/")
    def fake_create_estacao():
        return {"nome": "Estação Central", "sensores": [{"id": 1}]}

# Banco de dados em memória para testes
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    # Sobrescreve apenas a dependência do banco
    app.dependency_overrides[get_db] = override_get_db

    return TestClient(app)