from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import TipoParametro
from schemas.tipo_parametro import (
    TipoParametroCreate, 
    TipoParametroResponse, 
    TipoParametroUpdate,
)

router = APIRouter(prefix="/tipo_parametros", tags=["tipo parâmetros"])

@router.post("/", response_model=int)
def create_tipo_parametro(tipo_parametro: TipoParametroCreate, db: Session = Depends(get_db)) -> int:
    try:
        new_tipo_parametro = TipoParametro(**tipo_parametro.dict())
        db_tipo_parametro = db.query(TipoParametro).filter(TipoParametro.nome == new_tipo_parametro.nome).first()
        if db_tipo_parametro:
            raise HTTPException(status_code=400, detail="Tipo de parâmetro já existe.")
        db.add(new_tipo_parametro)
        db.commit()
        db.refresh(new_tipo_parametro)
        return new_tipo_parametro.id
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=list[TipoParametroResponse])
def list_all_tipo_parametros(db: Session = Depends(get_db)) -> list[TipoParametroResponse]:
    tipo_parametros = []
    try:
        db_tipo_parametros = db.query(TipoParametro).all()
        for db_tipo_parametro in db_tipo_parametros:
            tipo_parametros.append(TipoParametroResponse.from_orm(db_tipo_parametro))
        return tipo_parametros
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{tipo_parametro_id}", response_model=TipoParametroResponse)
def get_tipo_parametro_by_id(tipo_parametro_id: int, db: Session = Depends(get_db)) -> TipoParametroResponse:
    try:
        db_tipo_parametro = db.query(TipoParametro).filter(TipoParametro.id == tipo_parametro_id).first()
        if not db_tipo_parametro:
            raise HTTPException(status_code=404, detail="Tipo de parâmetro não encontrado.")
        return TipoParametroResponse.from_orm(db_tipo_parametro)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{tipo_parametro_id}", response_model=dict)
def update_tipo_parametro(tipo_parametro_id: int, tipo_parametro: TipoParametroUpdate, db: Session = Depends(get_db)) -> dict:
    try:
        db_tipo_parametro = db.query(TipoParametro).filter(TipoParametro.id == tipo_parametro_id).first()
        if not db_tipo_parametro:
            raise HTTPException(status_code=404, detail="Tipo de parâmetro não encontrado.")
        
        if tipo_parametro.nome is not None:
            db_tipo_parametro_by_nome = db.query(TipoParametro).filter(TipoParametro.nome == tipo_parametro.nome).first()
            if db_tipo_parametro_by_nome:
                raise HTTPException(status_code=400, detail="Tipo de parâmetro já existe com este nome.")

        for field, value in tipo_parametro.dict(exclude_unset=True).items():
            setattr(db_tipo_parametro, field, value)
        db.commit()
        return {"message": "Tipo de parâmetro atualizado com sucesso"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{tipo_parametro_id}", response_model=dict)
def delete_tipo_parametro(tipo_parametro_id: int, db: Session = Depends(get_db)) -> dict:
    try:
        db_tipo_parametro = db.query(TipoParametro).filter(TipoParametro.id == tipo_parametro_id).first()
        if not db_tipo_parametro:
            raise HTTPException(status_code=404, detail="Tipo de parâmetro não encontrado.")
        db.delete(db_tipo_parametro)
        db.commit()
        return {"message": "Tipo de parâmetro deletado com sucesso"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
