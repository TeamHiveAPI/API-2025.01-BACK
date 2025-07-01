import pytest
from fastapi.testclient import TestClient


class TestTipoParametroCRUD:
    """Testes de integração para CRUD de Tipo Parâmetro"""
    
    # def test_create_tipo_parametro(self, client: TestClient, auth_headers):
    #     """Teste de criação bem-sucedida de tipo parâmetro"""
    #     import uuid
    #     unique_name = f"Temperatura_Test_{str(uuid.uuid4())[:8]}"
    #     tipo_parametro_data = {
    #         "nome": unique_name,
    #         "descricao": "Medição de temperatura ambiente",
    #         "json": "test-integração"
    #     }
        
    #     response = client.post(
    #         "/tipo_parametros/",
    #         json=tipo_parametro_data,
    #         headers=auth_headers
    #     )
        
    #     # Verificar resposta
    #     assert response.status_code == 201, f"Expected 201, got {response.status_code}. Response: {response.text}"
    #     tipo_parametro_id = response.json()
    #     assert isinstance(tipo_parametro_id, int)
    #     assert tipo_parametro_id > 0
        
    # def test_create_parametro_success(self, client: TestClient, auth_headers):
    #     """Teste de criação bem-sucedida de parâmetro"""
    #     import uuid
        
    #     # Primeiro, criar um tipo_parametro
    #     unique_name = f"Temperatura_Test_{str(uuid.uuid4())[:8]}"
    #     tipo_parametro_data = {
    #         "nome": unique_name,
    #         "descricao": "Medição de temperatura ambiente",
    #         "json": "test-integração"
    #     }
        
    #     tipo_response = client.post(
    #         "/tipo_parametros/",
    #         json=tipo_parametro_data,
    #         headers=auth_headers
    #     )
        
    #     assert tipo_response.status_code == 201, f"Failed to create tipo_parametro: {tipo_response.text}"
    #     tipo_parametro_id = tipo_response.json()
        
    #     # Agora criar o parâmetro usando o ID do tipo_parametro
    #     unique_param_name = f"Param_Test_{str(uuid.uuid4())[:8]}"
    #     parametro_data = {
    #         "nome": unique_param_name,
    #         "unidade": "°C",
    #         "descricao": "Parâmetro de temperatura para teste",
    #         "quantidade_casas_decimais": 2,
    #         "fator_conversao": 1.0,
    #         "offset": 0.0,
    #         "tipo_parametro_id": tipo_parametro_id
    #     }
        
    #     response = client.post(
    #         "/parametros/",
    #         json=parametro_data,
    #         headers=auth_headers
    #     )
        
    #     # Verificar resposta
    #     assert response.status_code == 201, f"Expected 201, got {response.status_code}. Response: {response.text}"
    #     parametro_id = response.json()
    #     assert isinstance(parametro_id, int)
    #     assert parametro_id > 0
        
    #     # Verificar se o parâmetro foi criado corretamente fazendo um GET
    #     get_response = client.get(
    #         f"/parametros/{parametro_id}",
    #         headers=auth_headers
    #     )
        
    #     assert get_response.status_code == 200, f"Failed to get parametro: {get_response.text}"
    #     parametro_data_response = get_response.json()
    #     assert parametro_data_response["nome"] == unique_param_name
    #     assert parametro_data_response["unidade"] == "°C"
    #     assert parametro_data_response["tipo_parametro_id"] == tipo_parametro_id
        
    def test_create_estacao_and_add_parametro(self, client: TestClient, auth_headers):
        """Teste de criação de estação e adição de parâmetro"""
        import uuid
        
        # Primeiro, criar um tipo_parametro
        unique_tipo_name = f"Temperatura_Test_{str(uuid.uuid4())[:8]}"
        tipo_parametro_data = {
            "nome": unique_tipo_name,
            "descricao": "Medição de temperatura ambiente",
            "json": "test-integração"
        }
        
        tipo_response = client.post(
            "/tipo_parametros/",
            json=tipo_parametro_data,
            headers=auth_headers
        )
        
        assert tipo_response.status_code == 201, f"Failed to create tipo_parametro: {tipo_response.text}"
        tipo_parametro_id = tipo_response.json()
        
        # Criar um parâmetro
        unique_param_name = f"Param_Test_{str(uuid.uuid4())[:8]}"
        parametro_data = {
            "nome": unique_param_name,
            "unidade": "°C",
            "descricao": "Parâmetro de temperatura para teste",
            "quantidade_casas_decimais": 2,
            "fator_conversao": 1.0,
            "offset": 0.0,
            "tipo_parametro_id": tipo_parametro_id
        }
        
        param_response = client.post(
            "/parametros/",
            json=parametro_data,
            headers=auth_headers
        )
        
        assert param_response.status_code == 201, f"Failed to create parametro: {param_response.text}"
        parametro_id = param_response.json()
        
        # Criar uma estação sem sensores inicialmente
        unique_estacao_name = f"Estacao_Test_{str(uuid.uuid4())[:8]}"
        estacao_data = {
            "nome": unique_estacao_name,
            "cep": "12345-678",
            "rua": "Rua Teste",
            "bairro": "Bairro Teste",
            "cidade": "Cidade Teste",
            "numero": "123",
            "latitude": -23.5505,
            "longitude": -46.6333,
            "data_instalacao": "2025-07-01",
            "status": "ativa",
            "sensores": []
        }
        
        estacao_response = client.post(
            "/estacoes/",
            json=estacao_data,
            headers=auth_headers
        )
        
        assert estacao_response.status_code == 201, f"Failed to create estacao: {estacao_response.text}"
        estacao_created = estacao_response.json()
        assert "id" in estacao_created
        assert estacao_created["nome"] == unique_estacao_name
        assert estacao_created["status"] == "ativa"
        assert len(estacao_created["sensores"]) == 0
        
        estacao_id = estacao_created["id"]
        
        # Agora atualizar a estação para adicionar o parâmetro
        estacao_update_data = {
            "nome": unique_estacao_name,
            "cep": "12345-678",
            "rua": "Rua Teste",
            "bairro": "Bairro Teste",
            "cidade": "Cidade Teste",
            "numero": "123",
            "latitude": -23.5505,
            "longitude": -46.6333,
            "data_instalacao": "2025-07-01",
            "status": "ativa",
            "sensores": [parametro_id]
        }
        
        update_response = client.put(
            f"/estacoes/{estacao_id}",
            json=estacao_update_data,
            headers=auth_headers
        )
        
        assert update_response.status_code == 200, f"Failed to update estacao: {update_response.text}"
        estacao_updated = update_response.json()
        assert len(estacao_updated["sensores"]) == 1
        assert estacao_updated["sensores"][0]["id"] == parametro_id
        assert estacao_updated["sensores"][0]["nome"] == unique_param_name
        assert estacao_updated["sensores"][0]["unidade"] == "°C"
        
        # Verificar se a estação foi atualizada corretamente fazendo um GET
        get_estacao_response = client.get(
            f"/estacoes/uid/{estacao_updated['uid']}",
            headers=auth_headers
        )
        
        assert get_estacao_response.status_code == 200, f"Failed to get estacao: {get_estacao_response.text}"
        estacao_final = get_estacao_response.json()
        assert len(estacao_final["sensores"]) == 1
        assert estacao_final["sensores"][0]["id"] == parametro_id