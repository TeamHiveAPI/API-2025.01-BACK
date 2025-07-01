from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class TipoParametroCreate(BaseModel):
    nome: str
    descricao: str
    json: str

    model_config = ConfigDict(from_attributes=True)


class TipoParametroResponse(TipoParametroCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class TipoParametroUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    json: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)