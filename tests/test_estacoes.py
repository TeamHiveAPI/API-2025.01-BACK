# tests/test_estacoes.py

import pytest
from fastapi.testclient import TestClient

def test_create_estacao_success(client: TestClient):
    # Este teste agora usa o banco real da aplicação
    # Assumindo que já existem parâmetros no banco ou serão criados pelos testes de integração

    estacao_data = {
        "nome": "Estação Central",
        "cep": "12345-678",
        "rua": "Rua Principal",
        "bairro": "Centro",
        "cidade": "São Paulo",
        "numero": "100",
        "latitude": -23.5505,
        "longitude": -46.6333,
        "data_instalacao": "2025-01-01",
        "status": "ativa",
        "sensores": [1]
    }

    response = client.post("/estacoes/", json=estacao_data)

    assert response.status_code == 200
    body = response.json()
    assert body["nome"] == "Estação Central"
    assert isinstance(body["sensores"], list)
    assert len(body["sensores"]) == 1
    assert body["sensores"][0]["id"] == 1
