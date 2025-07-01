import sys
import os

# Adicionar o diretório raiz do projeto ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta

# Importações do projeto
from database import Base, get_db
from main import app
from core.security import get_password_hash, create_access_token
from core.config import settings
from models import Usuario as UsuarioModel

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def client():
    """Fixture que cria um cliente de teste usando o banco real da aplicação"""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def auth_headers():
    """Fixture que retorna headers de autenticação usando usuário existente"""
    # Usar o usuário de teste que já existe no banco
    # (criado pelo script create_test_user_and_token.py)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": "teste@email.com",
            "user_nivel": "ADMINISTRADOR",
            "user_id": 1,  # Assumindo que é o primeiro usuário
        },
        expires_delta=access_token_expires
    )
    
    return {"Authorization": f"Bearer {access_token}"}