from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from sqlalchemy.orm import Session
from database import get_db
from models import Usuario
from schemas.usuario import UsuarioCreateInput, UsuarioResponse, UsuarioUpdate

router = APIRouter(prefix="/usuarios", tags=["usuários"])
@router.post("/", response_model=UsuarioResponse)
def create_usuario(usuario_input: UsuarioCreateInput, db: Session = Depends(get_db)):
    usuario_dict = usuario_input.dict()
    usuario_dict["nivel_acesso"] = "ADMINISTRADOR"
    usuario_dict["data_criacao"] = datetime.now()

    db_usuario = Usuario(**usuario_dict)
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

@router.get("/", response_model=list[UsuarioResponse])
def list_usuarios(db: Session = Depends(get_db)):
    return db.query(Usuario).all()

@router.get("/{usuario_id}", response_model=UsuarioResponse)
def get_usuario(usuario_id: int, db: Session = Depends(get_db)):
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return db_usuario

@router.put("/{usuario_id}", response_model=UsuarioResponse)
def update_usuario(usuario_id: int, usuario: UsuarioUpdate, db: Session = Depends(get_db)):
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    for key, value in usuario.dict(exclude_unset=True).items():
        setattr(db_usuario, key, value)
    
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

@router.delete("/{usuario_id}")
def delete_usuario(usuario_id: int, db: Session = Depends(get_db)):
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    db.delete(db_usuario)
    db.commit()
    return {"message": "Usuário deletado com sucesso"}