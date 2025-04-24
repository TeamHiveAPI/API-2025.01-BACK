from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Alerta
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