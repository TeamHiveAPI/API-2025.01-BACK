# subscriber.py
import os
import json
import time
import logging
from datetime import datetime
import paho.mqtt.client as mqtt
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Configurações
MQTT_BROKER = 'localhost'
MQTT_PORT = 1883
MQTT_TOPIC = 'api-fatec/estacao/dados/'

# URI do MongoDB (pode vir de variável de ambiente)
MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://tmadm:apifatec2025@api-estacao.xikvdt1.mongodb.net/?retryWrites=true&w=majority')
MONGO_DB = 'api_estacao'
MONGO_COLLECTION = 'dados_estacao'
MONGO_FAILED = 'failed_messages'

# Setup de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# Conexão MongoDB
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[MONGO_DB]
collection = db[MONGO_COLLECTION]
failed_collection = db[MONGO_FAILED]

def retry_mongodb_insert(data, max_retries=3, delay=1):
    """
    Tenta inserir no MongoDB até max_retries vezes antes de salvar em failed_messages.
    """
    for attempt in range(1, max_retries + 1):
        try:
            collection.insert_one(data)
            logging.info(f"Inserido no MongoDB na tentativa {attempt}")
            return True
        except PyMongoError as e:
            logging.error(f"Tentativa {attempt} falhou: {e}")
            time.sleep(delay)
    # Se todas falharem
    failed_collection.insert_one({
        "data": data,
        "timestamp": datetime.utcnow(),
        "error_count": max_retries
    })
    logging.error("Todas as tentativas falharam, salvo em failed_messages")
    return False

# Callbacks MQTT
def on_connect(client, userdata, flags, rc):
    logging.info(f"Conectado ao broker MQTT com código {rc}")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        logging.info(f"Recebido no tópico {msg.topic}: {payload}")
        # Adiciona campo de controle
        payload['processado'] = False
        success = retry_mongodb_insert(payload)
        if success:
            logging.info("Dados salvos no MongoDB com sucesso")
        else:
            logging.error("Falha ao salvar dados no MongoDB")
    except Exception as e:
        logging.error(f"Erro ao processar mensagem MQTT: {e}")

if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    print("Iniciando subscriber MQTT...")
    client.loop_forever()