from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Estacao
from schemas.estacao import EstacaoCreate, EstacaoResponse
from typing import List

router = APIRouter(prefix="/estacoes", tags=["estações"])

@router.post("/", response_model=EstacaoResponse)
def create_estacao(estacao: EstacaoCreate, db: Session = Depends(get_db)):
    db_estacao = Estacao(
        nome=estacao.nome,
        cep=estacao.cep,
        rua=estacao.rua,
        bairro=estacao.bairro,
        cidade=estacao.cidade,
        numero=estacao.numero,
        latitude=estacao.latitude,
        longitude=estacao.longitude,
        data_instalacao=estacao.data_instalacao,
        status=estacao.status
    )
    db.add(db_estacao)
    db.commit()
    db.refresh(db_estacao)
    return db_estacao

@router.put("/{estacao_id}", response_model=EstacaoResponse)
def update_estacao(estacao_id: int, estacao: EstacaoCreate, db: Session = Depends(get_db)):
    db_estacao = db.query(Estacao).filter(Estacao.id == estacao_id).first()
    if not db_estacao:
        raise HTTPException(status_code=404, detail="Estação não encontrada")
    
    for key, value in estacao.dict().items():
        setattr(db_estacao, key, value)
    
    db.commit()
    db.refresh(db_estacao)
    return db_estacao

@router.get("/", response_model=List[EstacaoResponse])
def read_estacoes(db: Session = Depends(get_db)):
    estacoes = db.query(Estacao).all()
    return estacoes

@router.delete("/{estacao_id}", status_code=204)
def delete_estacao(estacao_id: int, db: Session = Depends(get_db)):
    db_estacao = db.query(Estacao).filter(Estacao.id == estacao_id).first()
    if not db_estacao:
        raise HTTPException(status_code=404, detail="Estação não encontrada")
    db.delete(db_estacao)
    db.commit()
    return None