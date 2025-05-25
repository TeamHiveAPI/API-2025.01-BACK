from fastapi import FastAPI, Depends
from database import get_db
from sqlalchemy.orm import Session

app = FastAPI()

@app.post("/estacoes/")
def create_estacao(estacao_data: dict, db: Session = Depends(get_db)):
    # Simula a lógica do endpoint
    return {
        "nome": estacao_data.get("nome"),
        "sensores": [{"id": id} for id in estacao_data.get("sensores", [])]
    }