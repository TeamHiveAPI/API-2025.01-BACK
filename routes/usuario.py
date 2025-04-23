from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from sqlalchemy.orm import Session
from database import get_db
from models import Usuario
from schemas.usuario import UsuarioCreateInput, UsuarioResponse, UsuarioUpdate, UsuarioPublicResponse
from core.security import get_current_user, get_password_hash, require_user_nivel
from models import Usuario as UsuarioModel

router = APIRouter(prefix="/usuarios", tags=["usuários"])
@router.post("/", response_model=UsuarioResponse)
def create_usuario(usuario_input: UsuarioCreateInput, db: Session = Depends(get_db)):
    usuario_dict = usuario_input.dict()
    usuario_dict["nivel_acesso"] = "ADMINISTRADOR"
    usuario_dict["data_criacao"] = datetime.now()
    usuario_dict["senha"] = get_password_hash(usuario_dict["senha"])

    db_usuario = Usuario(**usuario_dict)
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

@router.get("/", response_model=list[UsuarioPublicResponse])
def list_usuarios(db: Session = Depends(get_db)):
    db_usuarios = db.query(Usuario).all()
    return [
        UsuarioPublicResponse(
            id=usuario.id,
            nome=usuario.nome,
            email=usuario.email,
            nivel_acesso=usuario.nivel_acesso,
            data_criacao=usuario.data_criacao
        )
        for usuario in db_usuarios
    ]

@router.get("/me", response_model=UsuarioResponse)
async def read_current_user(
    current_user: UsuarioModel = Depends(get_current_user)
):
    """Get current user's information"""
    return current_user

@router.get("/{usuario_id}", response_model=UsuarioPublicResponse)
def get_usuario(usuario_id: int, db: Session = Depends(get_db)):
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return UsuarioPublicResponse(
        id=db_usuario.id,
        nome=db_usuario.nome,
        email=db_usuario.email,
        nivel_acesso=db_usuario.nivel_acesso,
        data_criacao=db_usuario.data_criacao
    )

@router.put("/{usuario_id}", response_model=UsuarioResponse)
def update_usuario(usuario_id: int, usuario: UsuarioUpdate, db: Session = Depends(get_db)):
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    update_data = usuario.dict(exclude_unset=True)
    if "senha" in update_data:
        update_data["senha"] = get_password_hash(update_data.pop("senha"))
    
    for key, value in update_data.items():
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