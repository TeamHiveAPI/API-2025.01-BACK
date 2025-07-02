import sys
import os

# Adicionar o diretório raiz do projeto ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from datetime import datetime, timedelta

@pytest.fixture
def auth_headers():
    """Fixture que retorna headers de autenticação para testes unitários"""
    # Para testes unitários, usamos um token mock simples
    mock_token = "mock-jwt-token-for-unit-tests"
    return {"Authorization": f"Bearer {mock_token}"}

@pytest.fixture
def mock_user_data():
    """Fixture que retorna dados de usuário para testes"""
    return {
        "id": 1,
        "email": "teste@email.com",
        "nome": "Usuário Teste",
        "nivel": "ADMINISTRADOR"
    }

@pytest.fixture
def mock_estacao_data():
    """Fixture que retorna dados de estação para testes"""
    return {
        "nome": "Estação Teste",
        "cep": "12345-678",
        "latitude": -23.5505,
        "longitude": -46.6333,
        "data_instalacao": datetime.now(),
        "status": "ativa",
        "sensores": []
    }