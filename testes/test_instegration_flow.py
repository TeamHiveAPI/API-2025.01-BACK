# # /home/ubuntu/backend_fastapi_test_files/tests/test_integration_flow.py

# import pytest
# from httpx import AsyncClient
# from sqlalchemy.ext.asyncio import AsyncSession
# from datetime import date

# # Importar schemas Pydantic (ajuste os caminhos e nomes conforme seu projeto)
# # from schemas.estacao import EstacaoCreate, EstacaoOut # Exemplo

# # Marcar todos os testes neste arquivo para rodar com asyncio
# pytestmark = pytest.mark.asyncio

# # Token fixo fornecido pelo usuário para teste@teste.com
# FIXED_TEST_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0ZUB0ZXN0ZS5jb20iLCJ1c2VyX25pdmVsIjoiQURNSU5JU1RSQURPUiIsInVzZXJfaWQiOjEsImV4cCI6MTgzNDQ4OTcxOX0.scXUPRnZteu6J2Uvit6QYhmF3XgSMK5ymknu7-kDXXk"

# async def test_station_creation_flow(client: AsyncClient, db_session: AsyncSession):
#     """Testa o fluxo: criar estação usando o token fixo."""
    
#     # Dados de exemplo para criar uma estação
#     station_data = {
#         "nome": "Estação Teste Integração",
#         "cep": "12345-678",
#         "rua": "Rua dos Testes",
#         "bairro": "Bairro da Integração",
#         "cidade": "Cidade Exemplo",
#         "numero": "123",
#         "latitude": -23.5505,
#         "longitude": -46.6333,
#         "data_instalacao": date.today().isoformat(), # Usa a data atual
#         "status": "ativa",
#         "sensores": [] # Sensores são adicionados depois, conforme informado
#     }
#     created_station_id = None

#     # --- 1. Criar Estação (Autenticado com Token Fixo) --- 
#     # Assumindo um endpoint POST /estacoes que recebe EstacaoCreate e retorna EstacaoOut
#     # e requer autenticação via Bearer token.
#     headers = {"Authorization": f"Bearer {FIXED_TEST_TOKEN}"}
#     print(f"\nUsando Header: {headers}") # Log para depuração
    
#     response = await client.post("/estacoes", json=station_data, headers=headers)
    
#     # Verifique o status code esperado (201 Created ou 200 OK)
#     assert response.status_code == 201, f"Erro ao criar estação: {response.text}"
#     created_station = response.json()
#     assert created_station["nome"] == station_data["nome"]
#     assert created_station["cep"] == station_data["cep"]
#     assert created_station["status"] == station_data["status"]
#     assert "id" in created_station
#     created_station_id = created_station["id"]
#     print(f"Estação criada com ID: {created_station_id}")

#     # --- 2. Opcional: Verificar Criação (GET /estacoes/{id} ou GET /estacoes) --- 
#     # Se você tiver uma rota GET para buscar a estação criada, podemos adicionar a verificação aqui.
#     # Exemplo com GET /estacoes/{id}:
#     # if created_station_id:
#     #     print(f"Verificando estação criada com ID: {created_station_id}")
#     #     get_response = await client.get(f"/estacoes/{created_station_id}", headers=headers)
#     #     assert get_response.status_code == 200, f"Erro ao buscar estação {created_station_id}: {get_response.text}"
#     #     fetched_station = get_response.json()
#     #     assert fetched_station["id"] == created_station_id
#     #     assert fetched_station["nome"] == station_data["nome"]
#     #     print(f"Estação {created_station_id} verificada com sucesso.")
#     # else:
#     #     print("Não foi possível verificar a estação criada (ID não obtido).")

# # --- Testes Adicionais --- 

# async def test_create_station_unauthenticated(client: AsyncClient):
#     """Testa a tentativa de criar estação sem token."""
#     station_data = {"nome": "Unauthorized Station", "cep": "00000-000", "rua": "-", "bairro": "-", "cidade": "-", "numero": "-", "latitude": 0, "longitude": 0, "data_instalacao": date.today().isoformat(), "status": "inativa", "sensores": []}
#     response = await client.post("/estacoes", json=station_data)
#     assert response.status_code == 401 # Unauthorized
#     # A resposta de erro pode variar, ajuste conforme sua API
#     # assert "detail" in response.json()
#     # assert response.json()["detail"] == "Not authenticated"

# # Adicione mais testes conforme necessário para outras rotas autenticadas
# # (ex: POST /tipo_parametros, POST /parametros, PUT /estacoes/{id}),
# # validações de dados, permissões, etc., sempre usando o FIXED_TEST_TOKEN.

