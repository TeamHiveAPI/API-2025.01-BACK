from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Medida, Estacao, Parametro
from schemas.medida import MedidaCreate, MedidaResponse, MedidaUpdate
from typing import List

router = APIRouter(prefix="/medidas", tags=["medidas"])

@router.post("/", response_model=MedidaResponse)
def create_medida(medida: MedidaCreate, db: Session = Depends(get_db)):
    try:
        # Verifica se a estação existe
        estacao = db.query(Estacao).filter(Estacao.id == medida.estacao_id).first()
        if not estacao:
            raise HTTPException(status_code=404, detail="Estação não encontrada")

        # Verifica se o parâmetro existe
        parametro = db.query(Parametro).filter(Parametro.id == medida.parametro_id).first()
        if not parametro:
            raise HTTPException(status_code=404, detail="Parâmetro não encontrado")

        # Cria a medida
        db_medida = Medida(
            estacao_id=medida.estacao_id,
            parametro_id=medida.parametro_id,
            valor=medida.valor,
            data_hora=medida.data_hora
        )
        db.add(db_medida)
        db.commit()
        db.refresh(db_medida)
        
        return db_medida

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[MedidaResponse])
def read_medidas(db: Session = Depends(get_db)):
    try:
        medidas = db.query(Medida).all()
        return medidas
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{medida_id}", response_model=MedidaResponse)
def read_medida(medida_id: int, db: Session = Depends(get_db)):
    try:
        medida = db.query(Medida).filter(Medida.id == medida_id).first()
        if not medida:
            raise HTTPException(status_code=404, detail="Medida não encontrada")
        return medida
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{medida_id}", response_model=MedidaResponse)
def update_medida(medida_id: int, medida: MedidaUpdate, db: Session = Depends(get_db)):
    try:
        db_medida = db.query(Medida).filter(Medida.id == medida_id).first()
        if not db_medida:
            raise HTTPException(status_code=404, detail="Medida não encontrada")

        # Se estação_id foi fornecido, verifica se existe
        if medida.estacao_id is not None:
            estacao = db.query(Estacao).filter(Estacao.id == medida.estacao_id).first()
            if not estacao:
                raise HTTPException(status_code=404, detail="Estação não encontrada")

        # Se parametro_id foi fornecido, verifica se existe
        if medida.parametro_id is not None:
            parametro = db.query(Parametro).filter(Parametro.id == medida.parametro_id).first()
            if not parametro:
                raise HTTPException(status_code=404, detail="Parâmetro não encontrado")

        # Atualiza os campos da medida
        for key, value in medida.dict(exclude_unset=True).items():
            setattr(db_medida, key, value)

        db.commit()
        db.refresh(db_medida)
        return db_medida

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{medida_id}", status_code=204)
def delete_medida(medida_id: int, db: Session = Depends(get_db)):
    try:
        db_medida = db.query(Medida).filter(Medida.id == medida_id).first()
        if not db_medida:
            raise HTTPException(status_code=404, detail="Medida não encontrada")
        
        db.delete(db_medida)
        db.commit()
        return None
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))