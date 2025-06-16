import os
import time
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Estacao, Medida, Parametro
from dotenv import load_dotenv
import logging

# Carrega variáveis de ambiente
load_dotenv()

# Configurações MongoDB
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://tmadm:apifatec2025@api-estacao.xikvdt1.mongodb.net/?retryWrites=true&w=majority"
)
MONGO_DB = "api_estacao"
COL_DADOS = "dados_estacao"

# Intervalo entre verificações
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 5))

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Conexão com Mongo
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client[MONGO_DB]
dados_coll = mongo_db[COL_DADOS]

def process_pending_documents():
    """
    Processa documentos no formato do ESP32:
    {
        "uid": "C86473D82240",
        "temp": 25.50,
        "umid": 60.00,
        "unixtime": 1747887187
    }
    """
    db: Session = SessionLocal()
    try:
        # Busca documentos não processados
        pending = list(dados_coll.find({"processado": False}))
        if not pending:
            return

        for doc in pending:
            uid = doc.get("uid")
            temp = doc.get("temp")
            umid = doc.get("umid")
            unixtime = doc.get("unixtime")
            lux= doc.get("lux")
            # Usa o offset fixo para o cálculo de chuva, sem depender de chuva_param
            chuva = None
            if doc.get("pulsos") is not None:
                try:
                    offset = 34  # Defina o valor fixo desejado aqui
                except (TypeError, ValueError):
                    offset = 0
                chuva = doc.get("pulsos") * offset
                chuva = chuva / 1000  # Converte mm³ para mm, se necessário
            # Validação básica
            if None in (uid, temp, umid, unixtime, lux, chuva):
                logging.warning(f"Documento incompleto: {doc}. Marcando como processado.")
                dados_coll.update_one(
                    {"_id": doc["_id"]},
                    {"$set": {"processado": True, "erro": "dados_incompletos"}}
                )
                continue

            # Verifica se a estação existe
            estacao = db.query(Estacao).filter_by(uid=uid).first()
            if not estacao:
                logging.warning(f"Estação {uid} não encontrada no Postgres")
                dados_coll.update_one(
                    {"_id": doc["_id"]},
                    {"$set": {"processado": True, "erro": "estacao_nao_encontrada"}}
                )
                continue

            # Obtém IDs dos parâmetros
            temp_param = db.query(Parametro).filter_by(nome="temperatura").first()
            umid_param = db.query(Parametro).filter_by(nome="umidade").first()
            lux_param = db.query(Parametro).filter_by(nome="luminosidade").first()
            chuva_param = db.query(Parametro).filter_by(nome="chuva").first()

            if not temp_param or not umid_param:
                logging.error("Parâmetros temperatura/umidade não configurados no banco")
                continue

            # Cria as medidas
            medidas = [
                Medida(
                    estacao_id=estacao.id,
                    parametro_id=temp_param.id,
                    valor=temp,
                    data_hora=datetime.fromtimestamp(unixtime)
                ),
                Medida(
                    estacao_id=estacao.id,
                    parametro_id=umid_param.id,
                    valor=umid,
                    data_hora=datetime.fromtimestamp(unixtime)
                ),
                  Medida(
                    estacao_id=estacao.id,
                    parametro_id=lux_param.id,
                    valor=lux,
                    data_hora=datetime.fromtimestamp(unixtime)
                ),
                  Medida(
                    estacao_id=estacao.id,
                    parametro_id=chuva_param.id,
                    valor=chuva,
                    data_hora=datetime.fromtimestamp(unixtime)
                )
            ]

            # Insere no PostgreSQL
            db.add_all(medidas)
            db.commit()
            logging.info(f"Dados processados para estação {uid} - Temp: {temp}°C, Umid: {umid}%, Lux: {lux} lux, Chuva: {chuva} mm")

            # Marca como processado no MongoDB
            dados_coll.update_one(
                {"_id": doc["_id"]},
                {"$set": {
                    "processado": True,
                    "processado_em": datetime.utcnow()
                }}
            )

    except PyMongoError as e:
        logging.error(f"Erro MongoDB: {e}")
    except Exception as e:
        db.rollback()
        logging.error(f"Erro PostgreSQL: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    logging.info("Iniciando serviço de migração Mongo → Postgres (formato ESP32)")
    while True:
        process_pending_documents()
        time.sleep(POLL_INTERVAL)