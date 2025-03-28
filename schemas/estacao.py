from pydantic import BaseModel
from enum import Enum
from datetime import date

class StatusEstacao(str, Enum):
    ativa = "ativa"
    inativa = "inativa"

class EstacaoCreate(BaseModel):
    nome: str
    cep: str
    rua: str
    bairro: str
    cidade: str
    numero: str
    latitude: float
    longitude: float
    data_instalacao: date
    status: StatusEstacao

class EstacaoResponse(EstacaoCreate):
    id: int

    class Config:
        orm_mode = True