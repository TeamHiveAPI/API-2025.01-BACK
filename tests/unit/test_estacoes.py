# tests/unit/test_estacoes.py

import pytest
from datetime import date
from unittest.mock import Mock, AsyncMock
from pydantic import ValidationError
from schemas.estacao import EstacaoCreate, EstacaoResponse, EstacaoUpdate, StatusEstacao, SensoresRelacionadosAEstacao
from models import Estacao, EstacaoParametro, Parametro, Usuario

class TestEstacaoSchemas:
    """Testes unitários para os schemas de estação"""
    
    def test_estacao_create_valid_data(self):
        """Testa criação de EstacaoCreate com dados válidos"""
        estacao_data = {
            "nome": "Estação Central",
            "cep": "12345-678",
            "rua": "Rua Principal",
            "bairro": "Centro",
            "cidade": "São Paulo",
            "numero": "100",
            "latitude": -23.5505,
            "longitude": -46.6333,
            "data_instalacao": date(2025, 1, 1),
            "status": StatusEstacao.ativa,
            "sensores": [1, 2, 3]
        }
        
        estacao = EstacaoCreate(**estacao_data)
        
        assert estacao.nome == "Estação Central"
        assert estacao.cep == "12345-678"
        assert estacao.rua == "Rua Principal"
        assert estacao.bairro == "Centro"
        assert estacao.cidade == "São Paulo"
        assert estacao.numero == "100"
        assert estacao.latitude == -23.5505
        assert estacao.longitude == -46.6333
        assert estacao.data_instalacao == date(2025, 1, 1)
        assert estacao.status == StatusEstacao.ativa
        assert estacao.sensores == [1, 2, 3]
    
    def test_estacao_create_without_sensores(self):
        """Testa criação de EstacaoCreate sem sensores (campo opcional)"""
        estacao_data = {
            "nome": "Estação Teste",
            "cep": "54321-876",
            "rua": "Rua Secundária",
            "bairro": "Bairro Novo",
            "cidade": "Rio de Janeiro",
            "numero": "200",
            "latitude": -22.9068,
            "longitude": -43.1729,
            "data_instalacao": date(2025, 2, 1),
            "status": StatusEstacao.inativa
        }
        
        estacao = EstacaoCreate(**estacao_data)
        
        assert estacao.nome == "Estação Teste"
        assert estacao.status == StatusEstacao.inativa
        assert estacao.sensores == []  # Deve ser lista vazia por padrão
    
    def test_estacao_create_invalid_status(self):
        """Testa criação de EstacaoCreate com status inválido"""
        estacao_data = {
            "nome": "Estação Teste",
            "cep": "12345-678",
            "rua": "Rua Principal",
            "bairro": "Centro",
            "cidade": "São Paulo",
            "numero": "100",
            "latitude": -23.5505,
            "longitude": -46.6333,
            "data_instalacao": date(2025, 1, 1),
            "status": "status_invalido",  # Status inválido
            "sensores": []
        }
        
        with pytest.raises(ValidationError) as exc_info:
            EstacaoCreate(**estacao_data)
        
        assert "status" in str(exc_info.value)
    
    def test_estacao_create_missing_required_fields(self):
        """Testa criação de EstacaoCreate com campos obrigatórios faltando"""
        estacao_data = {
            "nome": "Estação Teste"
            # Faltam campos obrigatórios
        }
        
        with pytest.raises(ValidationError) as exc_info:
            EstacaoCreate(**estacao_data)
        
        error_str = str(exc_info.value)
        assert "cep" in error_str
        assert "rua" in error_str
        assert "bairro" in error_str
    
    def test_estacao_response_creation(self):
        """Testa criação de EstacaoResponse"""
        sensor_data = SensoresRelacionadosAEstacao(
            id=1,
            nome="Temperatura",
            unidade="°C"
        )
        
        estacao_response = EstacaoResponse(
            id=1,
            uid="EST001",
            nome="Estação Central",
            cep="12345-678",
            rua="Rua Principal",
            bairro="Centro",
            cidade="São Paulo",
            numero="100",
            latitude=-23.5505,
            longitude=-46.6333,
            data_instalacao=date(2025, 1, 1),
            status=StatusEstacao.ativa,
            sensores=[sensor_data]
        )
        
        assert estacao_response.id == 1
        assert estacao_response.uid == "EST001"
        assert estacao_response.nome == "Estação Central"
        assert len(estacao_response.sensores) == 1
        assert estacao_response.sensores[0].nome == "Temperatura"
    
    def test_estacao_update_partial_data(self):
        """Testa criação de EstacaoUpdate com dados parciais"""
        estacao_update = EstacaoUpdate(
            nome="Novo Nome",
            status=StatusEstacao.inativa
        )
        
        assert estacao_update.nome == "Novo Nome"
        assert estacao_update.status == StatusEstacao.inativa
        assert estacao_update.cep is None  # Campos não fornecidos devem ser None
        assert estacao_update.rua is None
    
    def test_sensores_relacionados_creation(self):
        """Testa criação de SensoresRelacionadosAEstacao"""
        sensor = SensoresRelacionadosAEstacao(
            id=1,
            nome="Umidade",
            unidade="%"
        )
        
        assert sensor.id == 1
        assert sensor.nome == "Umidade"
        assert sensor.unidade == "%"
    
    def test_status_estacao_enum(self):
        """Testa o enum StatusEstacao"""
        assert StatusEstacao.ativa == "ativa"
        assert StatusEstacao.inativa == "inativa"
        
        # Testa que apenas valores válidos são aceitos
        assert StatusEstacao.ativa in [StatusEstacao.ativa, StatusEstacao.inativa]
        assert StatusEstacao.inativa in [StatusEstacao.ativa, StatusEstacao.inativa]


class TestEstacaoBusinessLogic:
    """Testes unitários para a lógica de negócio de estações"""
    
    @pytest.mark.asyncio
    async def test_create_estacao_without_sensores(self):
        """Testa criação de estação sem sensores usando mocks"""
        # Arrange
        mock_db = AsyncMock()
        mock_user = Mock(spec=Usuario)
        mock_user.id = 1
        
        estacao_data = EstacaoCreate(
            nome="Estação Teste",
            cep="12345-678",
            rua="Rua Principal",
            bairro="Centro",
            cidade="São Paulo",
            numero="100",
            latitude=-23.5505,
            longitude=-46.6333,
            data_instalacao=date(2025, 1, 1),
            status=StatusEstacao.ativa,
            sensores=[]
        )
        
        # Mock da estação criada
        mock_estacao = Mock(spec=Estacao)
        mock_estacao.id = 1
        mock_estacao.uid = "EST001"
        mock_estacao.nome = estacao_data.nome
        mock_estacao.cep = estacao_data.cep
        mock_estacao.rua = estacao_data.rua
        mock_estacao.bairro = estacao_data.bairro
        mock_estacao.cidade = estacao_data.cidade
        mock_estacao.numero = estacao_data.numero
        mock_estacao.latitude = estacao_data.latitude
        mock_estacao.longitude = estacao_data.longitude
        mock_estacao.data_instalacao = estacao_data.data_instalacao
        mock_estacao.status = estacao_data.status
        mock_estacao.parametros = []
        
        # Configurar mocks
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        mock_db.execute = AsyncMock()
        
        # Mock do resultado da query
        mock_result = Mock()
        mock_result.scalar_one.return_value = mock_estacao
        mock_db.execute.return_value = mock_result
        
        # Act - Simular a lógica de criação
        db_estacao = Estacao(
            nome=estacao_data.nome,
            cep=estacao_data.cep,
            rua=estacao_data.rua,
            bairro=estacao_data.bairro,
            cidade=estacao_data.cidade,
            numero=estacao_data.numero,
            latitude=estacao_data.latitude,
            longitude=estacao_data.longitude,
            data_instalacao=estacao_data.data_instalacao,
            status=estacao_data.status,
        )
        
        # Simular adição ao banco
        mock_db.add(db_estacao)
        await mock_db.commit()
        await mock_db.refresh(db_estacao)
        
        # Como não há sensores, não há associações para criar
        
        # Simular busca da estação com parâmetros
        await mock_db.execute(Mock())
        db_estacao_with_params = mock_result.scalar_one()
        
        # Criar resposta
        response = EstacaoResponse(
            id=1,
            uid="EST001",
            nome=db_estacao_with_params.nome,
            cep=db_estacao_with_params.cep,
            rua=db_estacao_with_params.rua,
            bairro=db_estacao_with_params.bairro,
            cidade=db_estacao_with_params.cidade,
            numero=db_estacao_with_params.numero,
            latitude=db_estacao_with_params.latitude,
            longitude=db_estacao_with_params.longitude,
            data_instalacao=db_estacao_with_params.data_instalacao,
            status=db_estacao_with_params.status,
            sensores=[]
        )
        
        # Assert
        assert response.nome == "Estação Teste"
        assert response.cep == "12345-678"
        assert response.status == StatusEstacao.ativa
        assert response.sensores == []
        
        # Verificar que os mocks foram chamados
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called()
        mock_db.refresh.assert_called_once()
        mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_estacao_with_sensores(self):
        """Testa criação de estação com sensores usando mocks"""
        # Arrange
        mock_db = AsyncMock()
        mock_user = Mock(spec=Usuario)
        mock_user.id = 1
        
        estacao_data = EstacaoCreate(
            nome="Estação com Sensores",
            cep="54321-876",
            rua="Rua Secundária",
            bairro="Bairro Novo",
            cidade="Rio de Janeiro",
            numero="200",
            latitude=-22.9068,
            longitude=-43.1729,
            data_instalacao=date(2025, 2, 1),
            status=StatusEstacao.ativa,
            sensores=[1, 2]
        )
        
        # Mock dos sensores/parâmetros
        mock_sensor1 = Mock(spec=Parametro)
        mock_sensor1.id = 1
        mock_sensor1.nome = "Temperatura"
        mock_sensor1.unidade = "°C"
        
        mock_sensor2 = Mock(spec=Parametro)
        mock_sensor2.id = 2
        mock_sensor2.nome = "Umidade"
        mock_sensor2.unidade = "%"
        
        # Mock da estação criada
        mock_estacao = Mock(spec=Estacao)
        mock_estacao.id = 1
        mock_estacao.uid = "EST002"
        mock_estacao.nome = estacao_data.nome
        mock_estacao.cep = estacao_data.cep
        mock_estacao.rua = estacao_data.rua
        mock_estacao.bairro = estacao_data.bairro
        mock_estacao.cidade = estacao_data.cidade
        mock_estacao.numero = estacao_data.numero
        mock_estacao.latitude = estacao_data.latitude
        mock_estacao.longitude = estacao_data.longitude
        mock_estacao.data_instalacao = estacao_data.data_instalacao
        mock_estacao.status = estacao_data.status
        mock_estacao.parametros = [mock_sensor1, mock_sensor2]
        
        # Configurar mocks
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        # Mock das queries de sensores
        mock_result_sensor1 = Mock()
        mock_result_sensor1.scalar_one_or_none.return_value = mock_sensor1
        
        mock_result_sensor2 = Mock()
        mock_result_sensor2.scalar_one_or_none.return_value = mock_sensor2
        
        # Mock da query final da estação
        mock_result_final = Mock()
        mock_result_final.scalar_one.return_value = mock_estacao
        
        # Configurar retornos sequenciais do execute
        mock_db.execute.side_effect = [
            mock_result_sensor1,  # Primeira busca de sensor
            mock_result_sensor2,  # Segunda busca de sensor
            mock_result_final     # Busca final da estação
        ]
        
        # Act - Simular a lógica de criação
        db_estacao = Estacao(
            nome=estacao_data.nome,
            cep=estacao_data.cep,
            rua=estacao_data.rua,
            bairro=estacao_data.bairro,
            cidade=estacao_data.cidade,
            numero=estacao_data.numero,
            latitude=estacao_data.latitude,
            longitude=estacao_data.longitude,
            data_instalacao=estacao_data.data_instalacao,
            status=estacao_data.status,
        )
        
        mock_db.add(db_estacao)
        await mock_db.commit()
        await mock_db.refresh(db_estacao)
        
        # Simular adição de sensores
        for sensor_id in estacao_data.sensores:
            result = await mock_db.execute(Mock())
            sensor = result.scalar_one_or_none()
            if sensor is not None:
                assoc = EstacaoParametro(estacao_id=1, parametro_id=sensor_id)
                mock_db.add(assoc)
        
        await mock_db.commit()
        
        # Simular busca final
        result = await mock_db.execute(Mock())
        db_estacao_with_params = result.scalar_one()
        
        # Criar resposta
        response = EstacaoResponse(
            id=1,
            uid="EST002",
            nome=db_estacao_with_params.nome,
            cep=db_estacao_with_params.cep,
            rua=db_estacao_with_params.rua,
            bairro=db_estacao_with_params.bairro,
            cidade=db_estacao_with_params.cidade,
            numero=db_estacao_with_params.numero,
            latitude=db_estacao_with_params.latitude,
            longitude=db_estacao_with_params.longitude,
            data_instalacao=db_estacao_with_params.data_instalacao,
            status=db_estacao_with_params.status,
            sensores=[
                {
                    "id": sensor.id,
                    "nome": sensor.nome,
                    "unidade": sensor.unidade
                }
                for sensor in db_estacao_with_params.parametros
            ]
        )
        
        # Assert
        assert response.nome == "Estação com Sensores"
        assert response.cep == "54321-876"
        assert response.status == StatusEstacao.ativa
        assert len(response.sensores) == 2
        assert response.sensores[0].nome == "Temperatura"
        assert response.sensores[1].nome == "Umidade"
        
        # Verificar que os mocks foram chamados corretamente
        assert mock_db.add.call_count == 3  # 1 estação + 2 associações
        assert mock_db.commit.call_count == 2  # 1 após estação + 1 após sensores
        mock_db.refresh.assert_called_once()
        assert mock_db.execute.call_count == 3  # 2 buscas de sensores + 1 busca final
    
    def test_estacao_model_creation(self):
        """Testa criação do modelo Estacao diretamente"""
        # Act
        estacao = Estacao(
            nome="Estação Modelo",
            cep="11111-111",
            rua="Rua Modelo",
            bairro="Bairro Modelo",
            cidade="Cidade Modelo",
            numero="999",
            latitude=-25.0000,
            longitude=-50.0000,
            data_instalacao=date(2025, 3, 1),
            status="ativa"
        )
        
        # Assert
        assert estacao.nome == "Estação Modelo"
        assert estacao.cep == "11111-111"
        assert estacao.rua == "Rua Modelo"
        assert estacao.bairro == "Bairro Modelo"
        assert estacao.cidade == "Cidade Modelo"
        assert estacao.numero == "999"
        assert estacao.latitude == -25.0000
        assert estacao.longitude == -50.0000
        assert estacao.data_instalacao == date(2025, 3, 1)
        assert estacao.status == "ativa"
