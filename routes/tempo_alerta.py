from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Alerta, AlertaDefinido, Estacao
from schemas.alerta import AlertaCreate, AlertaUpdate
from schemas.tempo_alerta import TempoAlertaResponse
from typing import List

from datetime import datetime

router = APIRouter(prefix="/tempo-em-alerta-por-estacao", tags=["tempo em alerta por estação"])

@router.get("/", response_model=List[TempoAlertaResponse])
def list_tempos_alerta(db: Session = Depends(get_db)):
    # Consulta para calcular o tempo total em alerta por estação, em horas
    resultados = db.query(
        Estacao.nome.label('estacao'),
        func.sum(
            func.coalesce(
                func.extract('epoch', Alerta.tempoFim) - func.extract('epoch', Alerta.data_hora), 0
            ) / 3600  # Convertendo de segundos para horas
        ).label('horas_alerta_total'),
        func.count(Alerta.id).label('qtd_alertas')
        ).join(AlertaDefinido, AlertaDefinido.id == Alerta.alerta_definido_id # Junção entre Alerta e AlertaDefinido
        ).join(Estacao, Estacao.id == AlertaDefinido.estacao_id  # Junção entre AlertaDefinido e Estacao
        ).group_by(Estacao.id).all()

    return [
        TempoAlertaResponse(estacao=estacao, horasAlerta=horas_alerta_total, qtdAlertas=qtd_alertas)
        for estacao, horas_alerta_total, qtd_alertas in resultados
    ]