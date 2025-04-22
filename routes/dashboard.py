from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Estacao, Parametro, AlertaDefinido, Usuario

# Definição do roteador
router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/contagem-entidades", response_model=dict)
def dashboard(db: Session = Depends(get_db)) -> dict:
    try:
        num_estacoes = db.query(Estacao).count()

        num_sensores = db.query(Parametro).count()

        num_alertas = db.query(AlertaDefinido).count()

        num_usuarios = db.query(Usuario).count()

        # Retorno das informações
        return {
            "numEstacoes": num_estacoes,
            "numSensores": num_sensores,
            "numAlertas": num_alertas,
            "numUsuarios": num_usuarios
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar requisição: {str(e)}")