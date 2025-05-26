from pydantic import BaseModel
from typing import Optional

class TipoParametroCreate(BaseModel):
    nome: str
    descricao: str
    json: str

class TipoParametroResponse(TipoParametroCreate):
    id: int

    class Config:
        from_attributes = True

class TipoParametroUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    json: Optional[str] = None