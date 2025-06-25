from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Alerta, AlertaDefinido, Estacao, Parametro, TipoParametro
from schemas.alerta import AlertaCreate, AlertaUpdate
from schemas.tempo_alerta import TempoAlertaResponse
from typing import List
from sqlalchemy import func, case
from pydantic import BaseModel

from datetime import datetime

class TotalAlertaTipoResponse(BaseModel):
    tipo_alerta: str
    total_alertas: int

router = APIRouter(prefix="/tempo-em-alerta-por-estacao", tags=["tempo em alerta por estação"])

@router.get("/", response_model=List[TempoAlertaResponse])
def list_tempos_alerta(db: Session = Depends(get_db)):
    # Adiciona logs para debug
    alertas = db.query(Alerta).all()
    print(f"Total de alertas: {len(alertas)}")
    
    alertas_definidos = db.query(AlertaDefinido).all()
    print(f"Total de alertas definidos: {len(alertas_definidos)}")
    
    estacoes = db.query(Estacao).all()
    print(f"Total de estações: {len(estacoes)}")

    # Query modificada para calcular o tempo corretamente
    resultados = db.query(
        Estacao.nome.label('estacao'),
        func.sum(
            case(
                # Se tempoFim é null, usa o timestamp atual
                (Alerta.tempoFim == None, 
                 func.extract('epoch', func.current_timestamp()) - func.extract('epoch', Alerta.data_hora)),
                # Senão, usa tempoFim - data_hora
                else_=func.extract('epoch', Alerta.tempoFim) - func.extract('epoch', Alerta.data_hora)
            ) / 3600  # Convertendo para horas
        ).label('horas_alerta_total'),
        func.count(Alerta.id).label('qtd_alertas')
    ).join(
        AlertaDefinido, AlertaDefinido.id == Alerta.alerta_definido_id
    ).join(
        Estacao, Estacao.id == AlertaDefinido.estacao_id
    ).group_by(Estacao.id, Estacao.nome).all()

    # Adiciona multiplicação por -1 se o valor for negativo
    resultados_corrigidos = [
        (
            estacao,
            horas_alerta_total * -1 if horas_alerta_total < 0 else horas_alerta_total,
            qtd_alertas
        )
        for estacao, horas_alerta_total, qtd_alertas in resultados
    ]

    print(f"Resultados corrigidos: {resultados_corrigidos}")

    return [
        TempoAlertaResponse(estacao=estacao, horasAlerta=float(horas_alerta_total) if horas_alerta_total else 0, qtdAlertas=qtd_alertas)
        for estacao, horas_alerta_total, qtd_alertas in resultados_corrigidos
    ]


    # Quantidade de alertas por tipo

@router.get("/total-por-tipo", response_model=List[TotalAlertaTipoResponse])
def list_total_alertas_por_tipo(db: Session = Depends(get_db)):
    resultados = db.query(
        TipoParametro.nome.label('tipo_alerta'),
        func.count(Alerta.id).label('total_alertas')
    ).join(
        AlertaDefinido, Alerta.alerta_definido_id == AlertaDefinido.id
    ).join(
        Parametro, AlertaDefinido.parametro_id == Parametro.id
    ).join(
        TipoParametro, Parametro.tipo_parametro_id == TipoParametro.id
    ).group_by(
        TipoParametro.nome
    ).all()

    return [
        TotalAlertaTipoResponse(
            tipo_alerta=tipo,
            total_alertas=total
        )
        for tipo, total in resultados
    ]