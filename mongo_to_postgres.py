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
    Busca documentos não processados no MongoDB, grava no Postgres e marca como processado.
    """
    db: Session = SessionLocal()
    try:
        pending = list(dados_coll.find({"processado": False}))
        if not pending:
            return

        for doc in pending:
            uid   = doc.get("uid")
            unixt = doc.get("unixtime")
            wind  = doc.get("wind")
            temp  = doc.get("temp")

            est = db.query(Estacao).filter_by(uid=uid).first()
            if not est:
                logging.warning(f"Estação com uid={uid} não encontrada no Postgres. Pulando.")
                dados_coll.update_one(
                    {"_id": doc["_id"]},
                    {"$set": {"processado": True, "erro": "estacao_nao_encontrada"}}
                )
                continue

            dt = datetime.fromtimestamp(unixt)
            medidas = []

            # Parâmetros suportados
            parametros_entrada = {
                "wind": wind,
                "temp": temp
            }

            for nome_param, valor in parametros_entrada.items():
                if valor is None:
                    continue
                param_id = _get_parametro_id(db, nome_param)
                if param_id is not None:
                    medidas.append(Medida(
                        estacao_id=est.id,
                        parametro_id=param_id,
                        valor=valor,
                        data_hora=dt
                    ))

            if medidas:
                db.add_all(medidas)
                db.commit()
                logging.info(f"Inseriu {len(medidas)} leituras para estação uid={uid} às {dt}")
            else:
                logging.warning(f"Nenhum parâmetro válido encontrado para uid={uid}")

            dados_coll.update_one(
                {"_id": doc["_id"]},
                {"$set": {"processado": True, "processado_em": datetime.utcnow()}}
            )

    except PyMongoError as e:
        logging.error(f"Erro ao acessar MongoDB: {e}")
    except Exception as e:
        db.rollback()
        logging.error(f"Erro ao gravar no Postgres: {e}")
    finally:
        db.close()

def _get_parametro_id(db: Session, nome_param: str) -> int | None:
    """
    Retorna o ID do parâmetro ou None se não existir no banco.
    """
    p = db.query(Parametro).filter(Parametro.nome == nome_param).first()
    if not p:
        logging.warning(f"Parâmetro '{nome_param}' não encontrado no Postgres. Ignorando.")
        return None
    return p.id

if __name__ == "__main__":
    logging.info("Iniciando serviço de migração Mongo → Postgres")
    while True:
        process_pending_documents()
        time.sleep(POLL_INTERVAL)
