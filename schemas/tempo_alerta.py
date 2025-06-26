from pydantic import BaseModel

class TempoAlertaResponse(BaseModel):
    estacao: str
    horasAlerta: float  # Tempo total em horas
    qtdAlertas: int

    class Config:
        from_attributes = True