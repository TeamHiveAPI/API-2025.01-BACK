# schemas/alerta_definido.py
from pydantic import BaseModel
from typing import Optional

class AlertaDefinidoCreate(BaseModel):
    estacao_id: int
    parametro_id: int
    condicao: str
    num_condicao: float   
    mensagem: str
    ativo: Optional[bool] = True

class AlertaDefinidoResponse(AlertaDefinidoCreate):
    id: int

    class Config:
        orm_mode = True

class AlertaDefinidoUpdate(BaseModel):
    estacao_id: Optional[int] = None
    parametro_id: Optional[int] = None
    condicao: Optional[str] = None
    num_condicao: Optional[float] = None   
    mensagem: Optional[str] = None
    ativo: Optional[bool] = None
