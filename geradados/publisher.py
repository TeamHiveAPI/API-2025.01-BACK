# publisher.py
import time
import json
import random
import paho.mqtt.publish as publish

# Configurações MQTT
MQTT_BROKER = 'localhost'
MQTT_PORT = 1883
MQTT_TOPIC = 'api-fatec/estacao/dados/'

def generate_test_data():
    """
    Gera dados de teste com fields:
      - uid: identificador da estação
      - unixtime: timestamp em segundos
      - wind: velocidade do vento (0-100)
      - temp: temperatura (15-35°C)
    """
    return {
       "uid": "4fc02475-47e1-4bda-bfe9-02294375983a",
       "unixtime": int(time.time()),
       "wind": round(random.uniform(0, 100), 2),
       "temp": round(random.uniform(15, 35), 2)
    }

if __name__ == "__main__":
    print("Iniciando publisher MQTT de teste...")
    while True:
        data = generate_test_data()
        payload = json.dumps(data)
        publish.single(
            MQTT_TOPIC,
            payload=payload,
            hostname=MQTT_BROKER,
            port=MQTT_PORT
        )
        print(f"Publicado: {payload} no tópico {MQTT_TOPIC}")
        time.sleep(5)
