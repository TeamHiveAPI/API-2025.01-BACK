# tests/test_estacoes.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from database import Base

def test_create_estacao_success(client: TestClient, db_session: Session):
    parametros_table = Base.metadata.tables["parametros"]
    db_session.execute(
        parametros_table.insert().values(
            id=1,
            nome="Temperatura",
            unidade="°C",
            descricao="",
            quantidade_casas_decimais=0,
            fator_conversao=1.0,
            offset=0.0,
            tipo_parametro_id=None
        )
    )
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

    response = client.post("/estacoes/", json=estacao_data)

    assert response.status_code == 200
    body = response.json()
    assert body["nome"] == "Estação Central"
    assert isinstance(body["sensores"], list)
    assert len(body["sensores"]) == 1
    assert body["sensores"][0]["id"] == 1
