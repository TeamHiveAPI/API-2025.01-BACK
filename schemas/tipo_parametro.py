from pydantic import BaseModel, Field
from typing import Optional

class TipoParametroCreate(BaseModel):
    nome: str
    descricao: str
    json_payload: str = Field(..., alias="json")

    class Config:
        allow_population_by_field_name = True


class TipoParametroResponse(TipoParametroCreate):
    id: int

    class Config:
        from_attributes = True


class TipoParametroUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    json_payload: Optional[str] = Field(None, alias="json")

    class Config:
        allow_population_by_field_name = True