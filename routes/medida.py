import logging
import json
from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload
from database import get_db
from models import Medida, Estacao, Parametro, AlertaDefinido, Alerta
from schemas.medida import MedidaCreate, MedidaResponse, MedidaUpdate
from typing import List
from datetime import datetime

router = APIRouter(prefix="/medidas", tags=["medidas"])

logger = logging.getLogger("medidas")
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(logging.DEBUG)

async def check_and_create_alertas(db: AsyncSession, medida: Medida, estacao: Estacao, parametro: Parametro):
    result_alertas_definidos = await db.execute(
        select(AlertaDefinido).where(
            AlertaDefinido.estacao_id == medida.estacao_id,
            AlertaDefinido.parametro_id == medida.parametro_id
        )
    )
    alertas_definidos = result_alertas_definidos.scalars().all()

    for alerta_def in alertas_definidos:
        result_alertas_ativos = await db.execute(
            select(Alerta).where(
                Alerta.alerta_definido_id == alerta_def.id,
                Alerta.tempoFim.is_(None)
            )
        )
        alertas_ativos = result_alertas_ativos.scalars().all()

        triggered = (
            (alerta_def.condicao == 'menor' and medida.valor < alerta_def.num_condicao) or
            (alerta_def.condicao == 'maior_igual' and medida.valor >= alerta_def.num_condicao) or
            (alerta_def.condicao == 'maior_que' and medida.valor > alerta_def.num_condicao)
        )

        if triggered:
            if not alertas_ativos:
                if alerta_def.condicao == 'menor':
                    titulo = f"{parametro.nome} menor que {alerta_def.num_condicao}{parametro.unidade}"
                elif alerta_def.condicao == 'maior_igual':
                    titulo = f"{parametro.nome} maior ou igual a {alerta_def.num_condicao}{parametro.unidade}"
                else:  # 'maior_que'
                    titulo = f"{parametro.nome} maior que {alerta_def.num_condicao}{parametro.unidade}"

                descricao = alerta_def.mensagem
                coordenadas_str = json.dumps([estacao.latitude, estacao.longitude])

                novo_alerta = Alerta(
                    alerta_definido_id=alerta_def.id,
                    titulo=titulo,
                    data_hora=medida.data_hora,
                    valor_medido=medida.valor,
                    descricaoAlerta=descricao,
                    estacao=estacao.nome,
                    coordenadas=coordenadas_str,
                    tempoFim=None
                )
                db.add(novo_alerta)

        else:
            for a in alertas_ativos:
                a.tempoFim = medida.data_hora

    await db.commit()

@router.post("/", response_model=MedidaResponse, status_code=status.HTTP_201_CREATED)
async def create_medida(medida: MedidaCreate, db: AsyncSession = Depends(get_db)):
    try:
        result_estacao = await db.execute(select(Estacao).where(Estacao.id == medida.estacao_id))
        estacao = result_estacao.scalar_one_or_none()
        if not estacao:
            raise HTTPException(status_code=404, detail="Estação não encontrada")

        result_parametro = await db.execute(select(Parametro).where(Parametro.id == medida.parametro_id))
        parametro = result_parametro.scalar_one_or_none()
        if not parametro:
            raise HTTPException(status_code=404, detail="Parâmetro não encontrado")

        db_medida = Medida(
            estacao_id=medida.estacao_id,
            parametro_id=medida.parametro_id,
            valor=medida.valor,
            data_hora=medida.data_hora or datetime.utcnow() 
        )
        db.add(db_medida)
        await db.flush() 

        await check_and_create_alertas(db, db_medida, estacao, parametro)

        await db.refresh(db_medida) 
        return db_medida

    except Exception as e:
        await db.rollback()
        logger.exception("Erro ao criar medida/alerta")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno do servidor")

@router.get("/", response_model=List[MedidaResponse])
async def read_medidas(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Medida))
        medidas = result.scalars().all()
        return medidas
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{medida_id}", response_model=MedidaResponse)
async def read_medida(medida_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Medida).where(Medida.id == medida_id))
        medida = result.scalar_one_or_none()
        if not medida:
            raise HTTPException(status_code=404, detail="Medida não encontrada")
        return medida
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/{medida_id}", response_model=MedidaResponse)
async def update_medida(medida_id: int, medida: MedidaUpdate, db: AsyncSession = Depends(get_db)):
    try:
        result_medida = await db.execute(select(Medida).where(Medida.id == medida_id))
        db_medida = result_medida.scalar_one_or_none()
        if not db_medida:
            raise HTTPException(status_code=404, detail="Medida não encontrada")

        if medida.estacao_id is not None:
            result_estacao = await db.execute(select(Estacao).where(Estacao.id == medida.estacao_id))
            estacao = result_estacao.scalar_one_or_none()
            if not estacao:
                raise HTTPException(status_code=404, detail="Estação não encontrada")

        if medida.parametro_id is not None:
            result_parametro = await db.execute(select(Parametro).where(Parametro.id == medida.parametro_id))
            parametro = result_parametro.scalar_one_or_none()
            if not parametro:
                raise HTTPException(status_code=404, detail="Parâmetro não encontrado")

        update_data = medida.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_medida, key, value)

        await db.commit()
        await db.refresh(db_medida)
        return db_medida

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.post("/lote", response_model=List[MedidaResponse], status_code=status.HTTP_201_CREATED)
async def create_medidas_lote( 
    medidas: List[MedidaCreate] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    criadas = []
    for medida in medidas:
        result_estacao = await db.execute(select(Estacao).where(Estacao.id == medida.estacao_id))
        estacao = result_estacao.scalar_one_or_none()
        if not estacao:
            raise HTTPException(status_code=404, detail=f"Estação com ID {medida.estacao_id} não encontrada para a medida de lote.")

        result_parametro = await db.execute(select(Parametro).where(Parametro.id == medida.parametro_id))
        parametro = result_parametro.scalar_one_or_none()
        if not parametro:
            raise HTTPException(status_code=404, detail=f"Parâmetro com ID {medida.parametro_id} não encontrado para a medida de lote.")

        db_medida = Medida(
            estacao_id=medida.estacao_id,
            parametro_id=medida.parametro_id,
            valor=medida.valor,
            data_hora=medida.data_hora or datetime.utcnow()
        )
        db.add(db_medida)
        await db.flush()

        await check_and_create_alertas(db, db_medida, estacao, parametro)
        criadas.append(db_medida)
    return criadas

@router.delete("/{medida_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medida(medida_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Medida).where(Medida.id == medida_id))
        db_medida = result.scalar_one_or_none()
        if not db_medida:
            raise HTTPException(status_code=404, detail="Medida não encontrada")

        await db.delete(db_medida)
        await db.commit()
        return None
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))