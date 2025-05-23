import requests
import time


TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0ZUB0ZXN0ZS5jb20iLCJ1c2VyX25pdmVsIjoiQURNSU5JU1RSQURPUiIsInVzZXJfaWQiOjEsImV4cCI6MTgzNDMxMjM3Mn0.-25aK5IzliTUG7l-ADIwS1SgLoXItz9ifSk6Ym-VRTw"
headers = {
    "Authorization": f"Bearer {TOKEN}"
}

BASE_URL = "http://localhost:8000"  # ajuste conforme o endereço do seu backend

def cadastrar_tipos_parametros():
    tipos_parametros = [
        {"nome": "Temperatura", "descricao": "Mede a temperatura ambiente", "json": "temp"},
        {"nome": "Vento", "descricao": "Mede a velocidade do vento", "json": "vento"},
        {"nome": "Umidade", "descricao": "Mede a umidade relativa do ar", "json": "umi"},
        {"nome": "Pressão", "descricao": "Mede a pressão atmosférica", "json": "atm"}
    ]

    for tipo in tipos_parametros:
        response = requests.post(f"{BASE_URL}/tipo_parametros", json=tipo, headers=headers)
        print(f"Cadastro de tipo {tipo['nome']} - Status: {response.status_code}")

def recuperar_tipos_parametros():
    response = requests.get(f"{BASE_URL}/tipo_parametros", headers=headers)
    if response.status_code == 200:
        print("Tipos de parâmetros recuperados com sucesso!")
        return response.json()
    else:
        print("Erro ao recuperar tipos de parâmetros:", response.status_code)
        return []

def cadastrar_parametros(tipo_nome_id_map):
    parametros = [
        {
            "nome": "Temperatura",
            "unidade": "C",
            "descricao": "Temperatura do ar em graus Celsius",
            "quantidade_casas_decimais": 2,
            "fator_conversao": 1,
            "offset": 0,
            "tipo_parametro_id": tipo_nome_id_map.get("Temperatura")
        },
        {
            "nome": "Vento",
            "unidade": "km/h",
            "descricao": "Velocidade do vento em km/h",
            "quantidade_casas_decimais": 2,
            "fator_conversao": 1,
            "offset": 0,
            "tipo_parametro_id": tipo_nome_id_map.get("Vento")
        },
        {
            "nome": "Umidade",
            "unidade": "%",
            "descricao": "Umidade relativa do ar",
            "quantidade_casas_decimais": 2,
            "fator_conversao": 1,
            "offset": 0,
            "tipo_parametro_id": tipo_nome_id_map.get("Umidade")
        },
        {
            "nome": "Pressão",
            "unidade": "hPa",
            "descricao": "Pressão atmosférica em hectopascais",
            "quantidade_casas_decimais": 2,
            "fator_conversao": 1,
            "offset": 0,
            "tipo_parametro_id": tipo_nome_id_map.get("Pressão")
        }
    ]

    for param in parametros:
        if param['tipo_parametro_id'] is None:
            print(f"Erro: tipo_parametro_id não encontrado para {param['nome']}")
            continue
        response = requests.post(f"{BASE_URL}/parametros", json=param, headers=headers)
        print(f"Cadastro de parâmetro {param['nome']} - Status: {response.status_code}")

def cadastrar_estacoes():
    estacoes = [
        {
            "nome": "Estação Norte",
            "cep": "01001-000",
            "rua": "Rua A",
            "bairro": "Centro",
            "cidade": "São Paulo",
            "numero": "100",
            "latitude": -23.5505,
            "longitude": -46.6333,
            "data_instalacao": "2025-05-23",
            "status": "ativa",
            "sensores": []
        },
        {
            "nome": "Estação Sul",
            "cep": "20000-000",
            "rua": "Rua B",
            "bairro": "Copacabana",
            "cidade": "Rio de Janeiro",
            "numero": "200",
            "latitude": -22.9707,
            "longitude": -43.1823,
            "data_instalacao": "2025-05-23",
            "status": "ativa",
            "sensores": []
        },
        {
            "nome": "Estação Leste",
            "cep": "30000-000",
            "rua": "Rua C",
            "bairro": "Savassi",
            "cidade": "Belo Horizonte",
            "numero": "300",
            "latitude": -19.9245,
            "longitude": -43.9352,
            "data_instalacao": "2025-05-23",
            "status": "ativa",
            "sensores": []
        },
        {
            "nome": "Estação Oeste",
            "cep": "40000-000",
            "rua": "Rua D",
            "bairro": "Pelourinho",
            "cidade": "Salvador",
            "numero": "400",
            "latitude": -12.9718,
            "longitude": -38.5011,
            "data_instalacao": "2025-05-23",
            "status": "ativa",
            "sensores": []
        },
        {
            "nome": "Estação Central",
            "cep": "70000-000",
            "rua": "Rua E",
            "bairro": "Asa Sul",
            "cidade": "Brasília",
            "numero": "500",
            "latitude": -15.7939,
            "longitude": -47.8828,
            "data_instalacao": "2025-05-23",
            "status": "ativa",
            "sensores": []
        }
    ]

    for estacao in estacoes:
        response = requests.post(f"{BASE_URL}/estacoes", json=estacao, headers=headers)
        print(f"Cadastro de {estacao['nome']} - Status: {response.status_code}")

def recuperar_parametros():
    response = requests.get(f"{BASE_URL}/parametros", headers=headers)
    if response.status_code == 200:
        print("Parâmetros recuperados com sucesso.")
        return response.json()
    else:
        print("Erro ao recuperar parâmetros:", response.status_code)
        return []

def recuperar_estacoes():
    response = requests.get(f"{BASE_URL}/estacoes", headers=headers)
    if response.status_code == 200:
        print("Estações recuperadas com sucesso.")
        return response.json()
    else:
        print("Erro ao recuperar estações:", response.status_code)
        return []

def atualizar_estacoes_com_sensores(estacoes, parametros):
    # sensores = [{"nome": f"Sensor de {p['nome']}", "unidade": p['unidade']} for p in parametros]
    sensores = [p['id'] for p in parametros]

    for estacao in estacoes:
        estacao_id = estacao['id']
        dados_atualizados = {
            "uid": estacao['uid'],
            "nome": estacao['nome'],
            "cep": estacao['cep'],
            "rua": estacao['rua'],
            "bairro": estacao['bairro'],
            "cidade": estacao['cidade'],
            "numero": estacao['numero'],
            "latitude": estacao['latitude'],
            "longitude": estacao['longitude'],
            "data_instalacao": estacao['data_instalacao'],
            "status": estacao['status'],
            "sensores": sensores
        }

        response = requests.put(f"{BASE_URL}/estacoes/{estacao_id}", json=dados_atualizados, headers=headers)
        print(f"Atualização da estação {estacao['nome']} (ID {estacao_id}) - Status: {response.status_code}")
        print(dados_atualizados)

# --- Execução sequencial ---

cadastrar_tipos_parametros()
tipos_cadastrados = recuperar_tipos_parametros()

# Mapeia nome → ID
tipo_nome_id_map = {tipo['nome']: tipo['id'] for tipo in tipos_cadastrados}

cadastrar_parametros(tipo_nome_id_map)
cadastrar_estacoes()

parametros = recuperar_parametros()
estacoes = recuperar_estacoes()

atualizar_estacoes_com_sensores(estacoes, parametros)
