import sys
import os

# Adicionar o diretório raiz do projeto ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient

# Importar a aplicação real
from main import app

@pytest.fixture
def client():
    """Fixture que cria um cliente de teste usando o banco real da aplicação"""
    with TestClient(app) as test_client:
        yield test_client