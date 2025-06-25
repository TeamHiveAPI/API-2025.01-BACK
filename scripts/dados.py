import requests
import random
from datetime import datetime, timedelta

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0ZUB0ZXN0ZS5jb20iLCJ1c2VyX25pdmVsIjoiQURNSU5JU1RSQURPUiIsInVzZXJfaWQiOjEsImV4cCI6MTgzNDMxMjM3Mn0.-25aK5IzliTUG7l-ADIwS1SgLoXItz9ifSk6Ym-VRTw"
headers = {
    "Authorization": f"Bearer {TOKEN}"
}

BASE_URL = "http://localhost:8000"

# def gerar_medidas(estacoes, parametros, coletas_por_dia=5, dias=365):
def gerar_medidas(estacoes, parametros, coletas_por_dia=5, dias=5):
    medidas = []
    hoje = datetime.now()
    data_inicio = hoje - timedelta(days=dias)
    intervalo_horas = 24 / coletas_por_dia  # Exemplo: 24/5 = ~4.8h entre coletas

    for estacao in estacoes:
        for parametro in parametros:
            data_atual = data_inicio

            for dia in range(dias):
                for coleta in range(coletas_por_dia):
                    # Gerar valor fictício baseado no parâmetro
                    if parametro['nome'] == "Temperatura":
                        valor = round(random.uniform(15, 35), 2)
                    elif parametro['nome'] == "Vento":
                        valor = round(random.uniform(0, 50), 2)
                    elif parametro['nome'] == "Umidade":
                        valor = round(random.uniform(20, 100), 2)
                    elif parametro['nome'] == "Pressão":
                        valor = round(random.uniform(950, 1050), 2)
                    else:
                        valor = round(random.uniform(0, 100), 2)

                    medida = {
                        "estacao_id": estacao['id'],
                        "parametro_id": parametro['id'],
                        "valor": valor,
                        "data_hora": data_atual.isoformat()
                    }

                    medidas.append(medida)
                    data_atual += timedelta(hours=intervalo_horas)

    return medidas

def enviar_medidas(medidas, lote=100):
    for i in range(0, len(medidas), lote):
        sublote = medidas[i:i+lote]
        for medida in sublote:
            response = requests.post(f"{BASE_URL}/medidas", json=medida, headers=headers)
            if response.status_code != 201:
                print(f"Erro ao enviar medida: {response.status_code} | {response.text}")
        print(f"{min(i+lote, len(medidas))}/{len(medidas)} medidas enviadas")

# --- Recuperar estacoes e parametros ---
def recuperar_estacoes():
    response = requests.get(f"{BASE_URL}/estacoes",headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("Erro ao recuperar estações:", response.status_code)
        return []

def recuperar_parametros():
    response = requests.get(f"{BASE_URL}/parametros", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("Erro ao recuperar parâmetros:", response.status_code)
        return []

# --- Execução ---
estacoes = recuperar_estacoes()
parametros = recuperar_parametros()

print("Gerando dados falsos...")
medidas = gerar_medidas(estacoes, parametros, coletas_por_dia=5, dias=10)
print(f"Total de medidas geradas: {len(medidas)}")

print("Enviando medidas...")
enviar_medidas(medidas, lote=100)  # Ajuste o tamanho do lote conforme capacidade do backend