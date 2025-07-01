from pydantic import BaseModel, ConfigDict, field_serializer
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
    model_config = ConfigDict(from_attributes=True) # Substitua class Config por model_config

    # Use @field_serializer para serializar campos específicos
    @field_serializer('data_hora')
    def serialize_data_hora(self, dt: datetime) -> float: 
        return dt.timestamp()
    
class MedidaUpdate(BaseModel):
    estacao_id: Optional[int] = None
    parametro_id: Optional[int] = None
    valor: Optional[float] = None
    data_hora: Optional[datetime] = None