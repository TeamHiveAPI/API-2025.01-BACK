from pydantic import BaseModel , ConfigDict
from typing import List, Optional
from datetime import date
from enum import Enum

class StatusEstacao(str, Enum):
    ativa = "ativa"
    inativa = "inativa"

class SensoresRelacionadosAEstacao(BaseModel):
    id: int
    nome: str
    unidade: str

class EstacaoResponse(BaseModel):
    id: int
    uid: str
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
    sensores: Optional[List[SensoresRelacionadosAEstacao]] = []

    model_config = ConfigDict(from_attributes=True)

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
    sensores: Optional[List[int]] = []

class EstacaoUpdate(BaseModel):
    uid: Optional[str] = None
    nome: Optional[str] = None
    cep: Optional[str] = None
    rua: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    numero: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    data_instalacao: Optional[date] = None
    status: Optional[StatusEstacao] = None
    sensores: Optional[List[int]] = []