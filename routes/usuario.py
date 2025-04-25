from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from sqlalchemy.orm import Session
from database import get_db
from models import Usuario
from schemas.usuario import UsuarioCreateInput, UsuarioResponse, UsuarioUpdate, UsuarioPublicResponse
from core.security import get_current_user, get_password_hash, require_user_nivel
from models import Usuario as UsuarioModel

from datetime import timedelta
from core.config import settings
from core.security import create_access_token
from schemas.token import Token

router = APIRouter(prefix="/usuarios", tags=["usuários"])
@router.post("/", response_model=Token)
def create_usuario(usuario_input: UsuarioCreateInput, db: Session = Depends(get_db)):
    usuario_dict = usuario_input.dict()
    usuario_dict["nivel_acesso"] = "ADMINISTRADOR"
    usuario_dict["data_criacao"] = datetime.now()
    usuario_dict["senha"] = get_password_hash(usuario_dict["senha"])

    db_usuario = Usuario(**usuario_dict)
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": db_usuario.email,
            "user_nivel": db_usuario.nivel_acesso,
            "user_id": db_usuario.id,
        },
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_email": db_usuario.email,
        "user_nivel": db_usuario.nivel_acesso,
        "user_id": db_usuario.id,
        "user_nome": db_usuario.nome
    }

@router.get("/", response_model=list[UsuarioPublicResponse])
def list_usuarios(
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user),
):
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

@router.get("/me", response_model=UsuarioPublicResponse)
async def read_current_user(
    current_user: UsuarioModel = Depends(get_current_user),
):
    return UsuarioPublicResponse(
        id=current_user.id,
        nome=current_user.nome,
        email=current_user.email,
        nivel_acesso=current_user.nivel_acesso,
        data_criacao=current_user.data_criacao
    )

@router.get("/{usuario_id}", response_model=UsuarioPublicResponse)
def get_usuario(
    usuario_id: int, db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user),
):
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
def update_usuario(
    usuario_id: int, usuario: UsuarioUpdate, 
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user),
):
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
def delete_usuario(
    usuario_id: int, 
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user),
):
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    db.delete(db_usuario)
    db.commit()
    return {"message": "Usuário deletado com sucesso"}