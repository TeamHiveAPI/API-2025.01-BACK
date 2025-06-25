from pydantic import BaseModel, Field
from typing import Optional

class TipoParametroCreate(BaseModel):
    nome: str
    descricao: str
    json_data: str = Field(alias='json', serialization_alias='json')  # Mapeia para a coluna 'json' do banco

class TipoParametroResponse(TipoParametroCreate):
    id: int

    class Config:
        from_attributes = True

class TipoParametroUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    json_data: Optional[str] = Field(default=None, alias='json', serialization_alias='json')  # Mapeia para a coluna 'json' do banco