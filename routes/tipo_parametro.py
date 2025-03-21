from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import TipoParametro
from schemas.tipo_parametro import TipoParametroCreate, TipoParametroResponse, TipoParametroUpdate

router = APIRouter(prefix="/tipo-parametros", tags=["tipo parâmetros"])

# Criar tipo de parâmetro
@router.post("/", response_model=TipoParametroResponse)
def create_tipo_parametro(tipo_parametro: TipoParametroCreate, db: Session = Depends(get_db)):
    db_tipo_parametro = TipoParametro(**tipo_parametro.dict())
    db.add(db_tipo_parametro)
    db.commit()
    db.refresh(db_tipo_parametro)
    return db_tipo_parametro