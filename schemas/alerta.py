from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AlertaCreate(BaseModel):
    alerta_definido_id: int
    data_hora: datetime
    valor_medido: float

class AlertaResponse(AlertaCreate):
    id: int

    class Config:
        orm_mode = True

class AlertaUpdate(BaseModel):
    alerta_definido_id: Optional[int] = None
    data_hora: Optional[datetime] = None
    valor_medido: Optional[float] = None