from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Parametro, Estacao, EstacaoParametro
from schemas.parametro import ParametroCreate, ParametroResponse, ParametroUpdate
from typing import List

router = APIRouter(prefix="/parametros", tags=["parâmetros"])

@router.post("/", response_model=int)
def create_parametro(parametro: ParametroCreate, db: Session = Depends(get_db)) -> int:
    try:
        new_parametro = Parametro(**parametro.dict())
        db_parametro = db.query(Parametro).filter(Parametro.nome == new_parametro.nome).first()
        if db_parametro:
            raise HTTPException(status_code=400, detail="Parâmetro já existe.")
        db.add(new_parametro)
        db.commit()
        db.refresh(new_parametro)
        return new_parametro.id
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[ParametroResponse])
def list_all_parametros(db: Session = Depends(get_db)) -> List[ParametroResponse]:
    try:
        db_parametros = db.query(Parametro).all()
        if not db_parametros:
            return []
        parametros = []
        for db_parametro in db_parametros:
            estacao_parametro = db.query(EstacaoParametro).filter(EstacaoParametro.parametro_id == db_parametro.id).first()
            estacao_nome = None
            if estacao_parametro:
                estacao = db.query(Estacao).filter(Estacao.id == estacao_parametro.estacao_id).first()
                if estacao:
                    estacao_nome = estacao.nome
            parametro = ParametroResponse(
                **db_parametro.__dict__,
                estacao_nome=estacao_nome
            )
            parametros.append(parametro)
        return parametros
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{parametro_id}", response_model=ParametroResponse)
def get_parametro_by_id(parametro_id: int, db: Session = Depends(get_db)) -> ParametroResponse:
    try:
        db_parametro = db.query(Parametro).filter(Parametro.id == parametro_id).first()
        if not db_parametro:
            raise HTTPException(status_code=404, detail="Parâmetro não encontrado.")
        return ParametroResponse.from_orm(db_parametro)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{parametro_id}", response_model=dict)
def update_parametro(parametro_id: int, parametro: ParametroUpdate, db: Session = Depends(get_db)) -> dict:
    try:
        db_parametro = db.query(Parametro).filter(Parametro.id == parametro_id).first()
        if not db_parametro:
            raise HTTPException(status_code=404, detail="Parâmetro não encontrado.")
        
        if parametro.nome is not None:
            db_parametro_by_nome = db.query(Parametro).filter(Parametro.nome == parametro.nome).first()
            if db_parametro_by_nome and db_parametro_by_nome.id != parametro_id:
                raise HTTPException(status_code=400, detail="Parâmetro já existe com este nome.")

        for field, value in parametro.dict(exclude_unset=True).items():
            setattr(db_parametro, field, value)
        db.commit()
        return {"message": "Parâmetro atualizado com sucesso"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{parametro_id}", response_model=dict)
def delete_parametro(parametro_id: int, db: Session = Depends(get_db)) -> dict:
    try:
        db_parametro = db.query(Parametro).filter(Parametro.id == parametro_id).first()
        if not db_parametro:
            raise HTTPException(status_code=404, detail="Parâmetro não encontrado.")
        db.delete(db_parametro)
        db.commit()
        return {"message": "Parâmetro deletado com sucesso"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))