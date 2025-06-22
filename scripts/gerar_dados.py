import requests

BASE_URL = "http://localhost:8000"  # ajuste conforme o endereço do seu backend

# --- 1. Cadastrar os tipos de parâmetros ---
tipos_parametros = [
    {"nome": "Temperatura", "descricao": "Mede a temperatura ambiente", "json": "temp"},
    {"nome": "Vento", "descricao": "Mede a velocidade do vento", "json": "vento"},
    {"nome": "Umidade", "descricao": "Mede a umidade relativa do ar", "json": "umi"},
    {"nome": "Pressão", "descricao": "Mede a pressão atmosférica", "json": "atm"}
]

for tipo in tipos_parametros:
    response = requests.post(f"{BASE_URL}/tipo_parametros", json=tipo)
    print(f"Cadastro de tipo {tipo['nome']} - Status: {response.status_code}")

# --- 2. Recuperar os tipos de parâmetros cadastrados ---
response = requests.get(f"{BASE_URL}/tipo_parametros")
if response.status_code == 200:
    tipos_cadastrados = response.json()
    print("Tipos de parâmetros recuperados com sucesso!")
else:
    print("Erro ao recuperar tipos de parâmetros:", response.status_code)
    tipos_cadastrados = []

# Mapear nomes para IDs
tipo_nome_id_map = {tipo['nome']: tipo['id'] for tipo in tipos_cadastrados}

# --- 3. Cadastrar os parâmetros associando com tipo_parametro_id ---
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
    response = requests.post(f"{BASE_URL}/parametros", json=param)
    print(f"Cadastro de parâmetro {param['nome']} - Status: {response.status_code}")


# Cadastro de 5 estações
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
        "status": "ativa",
        "sensores": []
    }
]

for estacao in estacoes:
    response = requests.post(f"{BASE_URL}/estacoes", json=estacao)
    print(f"Cadastro de {estacao['nome']} - Status: {response.status_code}")

# --- 1. Recuperar parâmetros ---
response = requests.get(f"{BASE_URL}/parametros")
if response.status_code == 200:
    parametros = response.json()
    print("Parâmetros recuperados com sucesso.")
else:
    print("Erro ao recuperar parâmetros:", response.status_code)
    parametros = []

# Montar sensores com base nos parâmetros
sensores = [{"nome": f"Sensor de {p['nome']}", "unidade": p['unidade']} for p in parametros]

# --- 2. Recuperar estações ---
response = requests.get(f"{BASE_URL}/estacoes")
if response.status_code == 200:
    estacoes = response.json()
    print("Estações recuperadas com sucesso.")
else:
    print("Erro ao recuperar estações:", response.status_code)
    estacoes = []

# --- 3. Atualizar cada estação com sensores ---
for estacao in estacoes:
    estacao_id = estacao['id']
    
    # Manter todos os campos obrigatórios + novos sensores
    dados_atualizados = {
        "nome": estacao['nome'],
        "cep": estacao['cep'],
        "rua": estacao['rua'],
        "bairro": estacao['bairro'],
        "cidade": estacao['cidade'],
        "numero": estacao['numero'],
        "latitude": estacao['latitude'],
        "longitude": estacao['longitude'],
        "status": estacao['status'],
        "sensores": sensores  # adicionando os sensores
    }
    
    response = requests.put(f"{BASE_URL}/estacoes/{estacao_id}", json=dados_atualizados)
    print(f"Atualização da estação {estacao['nome']} (ID {estacao_id}) - Status: {response.status_code}")
