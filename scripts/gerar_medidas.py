import random
from datetime import datetime, timedelta
import json

# Configurações
estacao_id = 1
parametro_id = 1
inicio = datetime(2025, 5, 4)  # Data inicial
dias = 21                      # Número de dias
current_id = 1

# Função para gerar horário aleatório dentro de um intervalo
def horario_aleatorio(inicio_hora, fim_hora):
    hora = random.randint(inicio_hora, fim_hora)
    minuto = random.randint(0, 59)
    return hora, minuto

# Função para gerar uma medida completa
def gerar_medida(dia, hora, minuto, valor, id_):
    dt = datetime(dia.year, dia.month, dia.day, hora, minuto)
    return {
        "estacao_id": estacao_id,
        "parametro_id": parametro_id,
        "valor": round(valor, 1),
        "data_hora": int(dt.timestamp()),
        "id": id_
    }

# Geração de medidas
medidas = []

for i in range(dias):
    dia = inicio + timedelta(days=i)
    valor_min = random.uniform(9, 14)
    valor_max = random.uniform(26, 31)
    valor_meio = random.uniform(valor_min + 1, valor_max - 1)
    valores = [valor_min, valor_meio, valor_max]

    # Gerar horários aleatórios por faixa
    faixas = [(0, 12), (13, 18), (19, 23)]
    for (ini, fim), valor in zip(faixas, valores):
        h, m = horario_aleatorio(ini, fim)
        medida = gerar_medida(dia, h, m, valor, current_id)
        medidas.append(medida)
        current_id += 1

# Salvar em arquivo
with open("medidas_aleatorias.json", "w") as f:
    json.dump(medidas, f, indent=2)

# Nota: o arquivo será salvo na pasta raíz, apenas copie o conteúdo e depois 
# Copie e cole o conteúdo do arquivo no Swagger, Postman, etc. e depois apague-o

print("Arquivo 'medidas_aleatorias.json' gerado com sucesso!")