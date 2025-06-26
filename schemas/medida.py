from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MedidaBase(BaseModel):
    estacao_id: int
    parametro_id: int
    valor: float
    data_hora: datetime

class MedidaCreate(MedidaBase):
    pass

class MedidaResponse(MedidaBase):
    id: int

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.timestamp()  # Converte para timestamp ao serializar
        }
class MedidaUpdate(BaseModel):
    estacao_id: Optional[int] = None
    parametro_id: Optional[int] = None
    valor: Optional[float] = None
    data_hora: Optional[datetime] = None