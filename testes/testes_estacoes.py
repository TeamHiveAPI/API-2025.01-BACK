import pytest
from httpx import AsyncClient

# Todos os testes deste arquivo são assíncronos
pytestmark = pytest.mark.asyncio

# Token de teste fixo (simula um usuário logado)
TEST_TOKEN = "eyJfake.token123"

async def test_listar_estacoes(client: AsyncClient):
    """Verifica se a rota GET /estacoes retorna uma lista válida."""
    # 1. Faz a requisição GET
    response = await client.get("/estacoes")
    
    # 2. Verifica o status code (200 = OK)
    assert response.status_code == 200
    
    # 3. Verifica se o corpo da resposta é uma lista
    estacoes = response.json()
    assert isinstance(estacoes, list), "A resposta deve ser uma lista de estações"

async def test_criar_estacao(client: AsyncClient):
    """Testa se a rota POST /estacoes cria uma estação corretamente."""
    # 1. Dados de exemplo para criar uma estação (sem o campo sensores)
    dados_estacao = {
        "nome": "Estação Meteorológica Central",
        "cep": "12345-678",
        "rua": "Rua das Flores",
        "bairro": "Centro",
        "cidade": "Cidade Exemplo",
        "numero": "100",
        "latitude": -23.5505,
        "longitude": -46.6333,
        "data_instalacao": "2025-06-24",
        "status": "ativa"
    }

    # 2. Faz a requisição POST com autenticação
    headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
    response = await client.post("/estacoes", json=dados_estacao, headers=headers)

    # 3. Verificações:
    assert response.status_code == 201, "Falha ao criar estação"  # 201 = Created
    resposta_json = response.json()
    assert resposta_json["nome"] == dados_estacao["nome"], "O nome da estação não bate"
    assert resposta_json["status"] == "ativa", "Status incorreto"
    assert "id" in resposta_json, "A estação criada deve ter um ID"
    assert resposta_json["cep"] == dados_estacao["cep"]
    assert resposta_json["rua"] == dados_estacao["rua"]
    assert resposta_json["bairro"] == dados_estacao["bairro"]
    assert resposta_json["cidade"] == dados_estacao["cidade"]
    assert resposta_json["numero"] == dados_estacao["numero"]
    assert float(resposta_json["latitude"]) == dados_estacao["latitude"]
    assert float(resposta_json["longitude"]) == dados_estacao["longitude"]
    assert resposta_json["data_instalacao"] == dados_estacao["data_instalacao"]
    assert isinstance(resposta_json["sensores"], list)

async def test_erro_autenticacao_post(client: AsyncClient):
    """Verifica se a rota POST /estacoes retorna erro 401 quando não autenticada."""
    response = await client.post("/estacoes", json={"nome": "Estação Não Autorizada"})
    assert response.status_code == 401, "Deveria exigir autenticação para POST"
