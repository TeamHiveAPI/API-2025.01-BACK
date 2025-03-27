from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UsuarioCreateInput(BaseModel):
    nome: str
    email: EmailStr
    senha: str

class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    nivel_acesso: str
    data_criacao: datetime

class UsuarioResponse(UsuarioCreate):
    id: int

    class Config:
        orm_mode = True

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    senha: Optional[str] = None
    nivel_acesso: Optional[str] = None
    data_criacao: Optional[datetime] = None