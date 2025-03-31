from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from enum import Enum

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
    sensores: Optional[List[int]] = []  # IDs dos sensores

class EstacaoResponse(EstacaoCreate):
    id: int

    class Config:
        orm_mode = True