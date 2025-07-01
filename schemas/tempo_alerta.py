from pydantic import BaseModel, ConfigDict

class TempoAlertaResponse(BaseModel):
    estacao: str
    horasAlerta: float  # Tempo total em horas
    qtdAlertas: int

    model_config = ConfigDict(from_attributes=True)