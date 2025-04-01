# routers/alertas_definidos.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import AlertaDefinido, Estacao, Parametro, EstacaoParametro
from schemas.alerta_definido import AlertaDefinidoCreate, AlertaDefinidoResponse, AlertaDefinidoUpdate

router = APIRouter(prefix="/alertas-definidos", tags=["alertas definidos"])

# Criar alerta definido
@router.post("/", response_model=AlertaDefinidoResponse)
def create_alerta_definido(alerta_definido: AlertaDefinidoCreate, db: Session = Depends(get_db)):
    # Verifica se a estação existe
    db_estacao = db.query(Estacao).filter(Estacao.id == alerta_definido.estacao_id).first()
    if not db_estacao:
        raise HTTPException(status_code=404, detail="Estação não encontrada")
    # Verifica se o sensor existe
    db_parametro = db.query(Parametro).filter(Parametro.id == alerta_definido.parametro_id).first()
    if not db_parametro:
        raise HTTPException(status_code=404, detail="Sensor (parâmetro) não encontrado")
    # Verifica se o sensor está vinculado à estação
    db_link = db.query(EstacaoParametro).filter(
        EstacaoParametro.estacao_id == alerta_definido.estacao_id,
        EstacaoParametro.parametro_id == alerta_definido.parametro_id
    ).first()
    if not db_link:
        raise HTTPException(status_code=400, detail="Sensor não vinculado à estação informada")

    db_alerta_definido = AlertaDefinido(**alerta_definido.dict())
    db.add(db_alerta_definido)
    db.commit()
    db.refresh(db_alerta_definido)
    return db_alerta_definido

# Listar todos os alertas definidos
@router.get("/", response_model=list[AlertaDefinidoResponse])
def list_alertas_definidos(db: Session = Depends(get_db)):
    return db.query(AlertaDefinido).all()

# Listar alerta definido específico por ID
@router.get("/{alerta_definido_id}", response_model=AlertaDefinidoResponse)
def get_alerta_definido(alerta_definido_id: int, db: Session = Depends(get_db)):
    db_alerta_definido = db.query(AlertaDefinido).filter(AlertaDefinido.id == alerta_definido_id).first()
    if not db_alerta_definido:
        raise HTTPException(status_code=404, detail="Alerta definido não encontrado")
    return db_alerta_definido

# Atualizar alerta definido específico por ID
@router.put("/{alerta_definido_id}", response_model=AlertaDefinidoResponse)
def update_alerta_definido(alerta_definido_id: int, alerta_definido: AlertaDefinidoUpdate, db: Session = Depends(get_db)):
    db_alerta_definido = db.query(AlertaDefinido).filter(AlertaDefinido.id == alerta_definido_id).first()
    if not db_alerta_definido:
        raise HTTPException(status_code=404, detail="Alerta definido não encontrado")
    
    # Se estiver atualizando estacao_id ou parametro_id, verificar a existência e o vínculo
    estacao_id = alerta_definido.estacao_id if alerta_definido.estacao_id is not None else db_alerta_definido.estacao_id
    parametro_id = alerta_definido.parametro_id if alerta_definido.parametro_id is not None else db_alerta_definido.parametro_id

    db_estacao = db.query(Estacao).filter(Estacao.id == estacao_id).first()
    if not db_estacao:
        raise HTTPException(status_code=404, detail="Estação não encontrada")
    db_parametro = db.query(Parametro).filter(Parametro.id == parametro_id).first()
    if not db_parametro:
        raise HTTPException(status_code=404, detail="Sensor (parâmetro) não encontrado")
    db_link = db.query(EstacaoParametro).filter(
        EstacaoParametro.estacao_id == estacao_id,
        EstacaoParametro.parametro_id == parametro_id
    ).first()
    if not db_link:
        raise HTTPException(status_code=400, detail="Sensor não vinculado à estação informada")
    
    for key, value in alerta_definido.dict(exclude_unset=True).items():
        setattr(db_alerta_definido, key, value)
    
    db.commit()
    db.refresh(db_alerta_definido)
    return db_alerta_definido

# Deletar alerta definido específico por ID
@router.delete("/{alerta_definido_id}")
def delete_alerta_definido(alerta_definido_id: int, db: Session = Depends(get_db)):
    db_alerta_definido = db.query(AlertaDefinido).filter(AlertaDefinido.id == alerta_definido_id).first()
    if not db_alerta_definido:
        raise HTTPException(status_code=404, detail="Alerta definido não encontrado")
    
    db.delete(db_alerta_definido)
    db.commit()
    return {"message": "Alerta definido deletado com sucesso"}
