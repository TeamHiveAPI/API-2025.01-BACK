from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Alerta
from typing import List
from schemas.alerta import AlertaCreate, AlertaResponse, AlertaUpdate
from core.security import get_current_user
from models import Usuario as UsuarioModel

router = APIRouter(prefix="/alertas", tags=["alertas"])

# Criar alerta
@router.post("/", response_model=AlertaResponse)
def create_alerta(
    alerta: AlertaCreate, 
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user),
):
    db_alerta = Alerta(**alerta.dict())
    db.add(db_alerta)
    db.commit()
    db.refresh(db_alerta)
    return db_alerta

# Listar todos os alertas
@router.get("/", response_model=list[AlertaResponse])
def list_alertas(db: Session = Depends(get_db)):
    return db.query(Alerta).all()

# Listar alerta específico por ID
@router.get("/{alerta_id}", response_model=AlertaResponse)
def get_alerta(alerta_id: int, db: Session = Depends(get_db)):
    db_alerta = db.query(Alerta).filter(Alerta.id == alerta_id).first()
    if not db_alerta:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    return db_alerta

# Atualizar alerta específico por ID
@router.put("/{alerta_id}", response_model=AlertaResponse)
def update_alerta(
    alerta_id: int, 
    alerta: AlertaUpdate, 
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user),
):
    db_alerta = db.query(Alerta).filter(Alerta.id == alerta_id).first()
    if not db_alerta:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    
    for key, value in alerta.dict(exclude_unset=True).items():
        setattr(db_alerta, key, value)
    
    db.commit()
    db.refresh(db_alerta)
    return db_alerta

# Deletar alerta específico por ID
@router.delete("/{alerta_id}")
def delete_alerta(
    alerta_id: int, 
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user),
):
    db_alerta = db.query(Alerta).filter(Alerta.id == alerta_id).first()
    if not db_alerta:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    
    db.delete(db_alerta)
    db.commit()
    return {"message": "Alerta deletado com sucesso"}

@router.get("/ativos", response_model=List[AlertaResponse])
def list_alertas_ativos(db: Session = Depends(get_db)):
    alertas_ativos = (
        db.query(Alerta)
        .filter(Alerta.tempoFim == None)  # Alertas sem tempoFim são considerados ativos
        .all()
    )

    return [
        AlertaResponse(
            id=alerta.id,
            alertaAtivo=True,
            titulo=alerta.titulo,
            data_hora=alerta.data_hora,
            valor_medido=alerta.valor_medido,
            descricaoAlerta=alerta.descricaoAlerta,
            estacao=alerta.estacao,
            coordenadas=list(map(float, alerta.coordenadas.strip("[]").split(","))),
            tempoFim=None,
            expandido=(alerta == alertas_ativos[0])
        )
        for alerta in alertas_ativos
    ]

@router.get("/passados", response_model=List[AlertaResponse])
def list_alertas_passados(db: Session = Depends(get_db)):
    alertas_passados = (
        db.query(Alerta)
        .filter(Alerta.tempoFim != None)  # Alertas com tempoFim são considerados passados
        .all()
    )

    return [
        AlertaResponse(
            id=alerta.id,
            alertaAtivo=False,
            titulo=alerta.titulo,
            data_hora=alerta.data_hora,
            valor_medido=alerta.valor_medido,
            descricaoAlerta=alerta.descricaoAlerta,
            estacao=alerta.estacao,
            coordenadas=list(map(float, alerta.coordenadas.strip("[]").split(","))),
            tempoFim=alerta.tempoFim,
            expandido=False
        )
        for alerta in alertas_passados
    ]

@router.get("/mais-recente", response_model=AlertaResponse)
def get_alerta_mais_recente(db: Session = Depends(get_db)):
    alerta = (
        db.query(Alerta)
        .order_by(Alerta.data_hora.desc())
        .first()
    )
    if not alerta:
        raise HTTPException(status_code=404, detail="Nenhum alerta encontrado")

    return AlertaResponse(
        id=alerta.id,
        alertaAtivo=True,
        titulo=alerta.titulo,
        data_hora=alerta.data_hora,
        valor_medido=alerta.valor_medido,
        descricaoAlerta=alerta.descricaoAlerta,
        estacao=alerta.estacao,
        coordenadas=list(map(float, alerta.coordenadas.strip("[]").split(","))),
        tempoFim=alerta.tempoFim,
        expandido=False
    )