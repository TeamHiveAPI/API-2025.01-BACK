import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from models import Parametro

def test_create_estacao_success(client: TestClient, db_session: Session):
    # Given: Configura um sensor no banco simulado
    sensor = Parametro(id=1, nome="Temperatura", unidade="°C")
    db_session.add(sensor)
    db_session.commit()

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

    # When: Faz a requisição POST
    response = client.post("/estacoes/", json=estacao_data)

    # Then: Verifica a resposta
    assert response.status_code == 200
    assert response.json()["nome"] == "Estação Central"
    assert len(response.json()["sensores"]) == 1
    assert response.json()["sensores"][0]["id"] == 1