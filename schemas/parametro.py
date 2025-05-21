import json
from pydantic import BaseModel
from typing import Optional

class ParametroCreate(BaseModel):
    nome: str
    unidade: str
    descricao: str
    quantidade_casas_decimais: int
    fator_conversao: float
    offset: float
    tipo_parametro_id: int
   

class ParametroResponse(ParametroCreate):
    id: int
    estacao_nome: Optional[str]

    class Config:
        from_attributes = True

class ParametroUpdate(BaseModel):
    nome: Optional[str] = None
    unidade: Optional[str] = None
    descricao: Optional[str] = None
    quantidade_casas_decimais: Optional[int] = None
    fator_conversao: Optional[float] = None
    offset: Optional[float] = None
    tipo_parametro_id: Optional[int] = None
    