from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models import Alerta, AlertaDefinido, Estacao, Parametro, TipoParametro
from schemas.alerta import AlertaCreate, AlertaUpdate
from schemas.tempo_alerta import TempoAlertaResponse
from typing import List
from sqlalchemy import func, case
from pydantic import BaseModel

from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(handler)


class TotalAlertaTipoResponse(BaseModel):
    tipo_alerta: str
    total_alertas: int

router = APIRouter(prefix="/tempo-em-alerta-por-estacao", tags=["tempo em alerta por estação"])

@router.get("/", response_model=List[TempoAlertaResponse])
async def list_tempos_alerta(db: AsyncSession = Depends(get_db)):
    try:
        result_alertas = await db.execute(select(Alerta))
        alertas = result_alertas.scalars().all()
        logger.info(f"Total de alertas: {len(alertas)}")
        
        result_alertas_definidos = await db.execute(select(AlertaDefinido))
        alertas_definidos = result_alertas_definidos.scalars().all()
        logger.info(f"Total de alertas definidos: {len(alertas_definidos)}")
        
        result_estacoes = await db.execute(select(Estacao))
        estacoes = result_estacoes.scalars().all()
        logger.info(f"Total de estações: {len(estacoes)}")

        stmt = select(
            Estacao.nome.label('estacao'),
            func.sum(
                case(
                    (Alerta.tempoFim == None, 
                     func.extract('epoch', func.now()) - func.extract('epoch', Alerta.data_hora)),
                    else_=func.extract('epoch', Alerta.tempoFim) - func.extract('epoch', Alerta.data_hora)
                ) / 3600
            ).label('horas_alerta_total'),
            func.count(Alerta.id).label('qtd_alertas')
        ).join(
            AlertaDefinido, AlertaDefinido.id == Alerta.alerta_definido_id
        ).join(
            Estacao, Estacao.id == AlertaDefinido.estacao_id
        ).group_by(Estacao.id, Estacao.nome)

        result_query = await db.execute(stmt)
        resultados = result_query.all()

        resultados_corrigidos = [
            (
                estacao,
                horas_alerta_total * -1 if horas_alerta_total and horas_alerta_total < 0 else horas_alerta_total,
                qtd_alertas
            )
            for estacao, horas_alerta_total, qtd_alertas in resultados
        ]

        logger.info(f"Resultados corrigidos: {resultados_corrigidos}")

        return [
            TempoAlertaResponse(estacao=estacao, horasAlerta=float(horas_alerta_total) if horas_alerta_total else 0, qtdAlertas=qtd_alertas)
            for estacao, horas_alerta_total, qtd_alertas in resultados_corrigidos
        ]
    except Exception as e:
        logger.exception("Erro ao listar tempos de alerta")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao processar requisição: {str(e)}")

@router.get("/total-por-tipo", response_model=List[TotalAlertaTipoResponse])
async def list_total_alertas_por_tipo(db: AsyncSession = Depends(get_db)):
    try:
        stmt = select(
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
        )
        result_query = await db.execute(stmt)
        resultados = result_query.all()

        return [
            TotalAlertaTipoResponse(
                tipo_alerta=tipo,
                total_alertas=total
            )
            for tipo, total in resultados
        ]
    except Exception as e:
        logger.exception("Erro ao listar total de alertas por tipo")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao processar requisição: {str(e)}")