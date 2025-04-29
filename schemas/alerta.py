from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# Modelo para criação de um alerta
class AlertaCreate(BaseModel):
    alerta_definido_id: int
    data_hora: datetime
    valor_medido: float
    titulo: str
    descricaoAlerta: str
    estacao: str
    coordenadas: List[float]
    tempoFim: Optional[datetime] = None

# Modelo para resposta de um alerta
class AlertaResponse(AlertaCreate):
    id: int
    alertaAtivo: bool
    expandido: bool

    class Config:
        orm_mode = True

# Modelo para atualização de um alerta
class AlertaUpdate(BaseModel):
    alerta_definido_id: Optional[int] = None
    data_hora: Optional[datetime] = None
    valor_medido: Optional[float] = None
    titulo: Optional[str] = None
    descricaoAlerta: Optional[str] = None
    estacao: Optional[str] = None
    coordenadas: Optional[List[float]] = None
    tempoFim: Optional[datetime] = None