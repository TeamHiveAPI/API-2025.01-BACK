from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Parametro
from schemas.parametro import ParametroCreate, ParametroResponse, ParametroUpdate

router = APIRouter(prefix="/parametros", tags=["parâmetros"])

# Criar parâmetro
@router.post("/", response_model=ParametroResponse)
def create_parametro(parametro: ParametroCreate, db: Session = Depends(get_db)):
    db_parametro = Parametro(**parametro.dict())
    db.add(db_parametro)
    db.commit()
    db.refresh(db_parametro)
    return db_parametro