# routers/medida.py
import logging
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_db
# Importar os modelos necessários
from models import Medida, Estacao, Parametro, AlertaDefinido, Alerta
from schemas.medida import MedidaCreate, MedidaResponse, MedidaUpdate
from typing import List
# Você pode precisar importar datetime se não estiver já globalmente disponível
from datetime import datetime

router = APIRouter(prefix="/medidas", tags=["medidas"])

# Configura um logger para capturar exceptions
logger = logging.getLogger("medidas")
# Se ainda não houver handler, adiciona um básico (stdout) — ajusta nível conforme desejado
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
    result = await db.execute(
        db.query(AlertaDefinido).filter(
            AlertaDefinido.estacao_id == medida.estacao_id,
            AlertaDefinido.parametro_id == medida.parametro_id
        )
    )
    alertas_definidos = result.scalars().all()

    for alerta_def in alertas_definidos:
        result = await db.execute(
            db.query(Alerta).filter(
                Alerta.alerta_definido_id == alerta_def.id,
                Alerta.tempoFim.is_(None)
            )
        )
        alertas_ativos = result.scalars().all()

        # checa a condição
        triggered = (
            (alerta_def.condicao == 'menor' and medida.valor < alerta_def.num_condicao) or
            (alerta_def.condicao == 'maior_igual' and medida.valor >= alerta_def.num_condicao) or
            (alerta_def.condicao == 'maior_que' and medida.valor > alerta_def.num_condicao)
        )

        if triggered:
            if not alertas_ativos:
                # --- aqui mudamos o título para o padrão curto ---
                if alerta_def.condicao == 'menor':
                    titulo = f"{parametro.nome} menor que {alerta_def.num_condicao}{parametro.unidade}"
                elif alerta_def.condicao == 'maior_igual':
                    titulo = f"{parametro.nome} maior ou igual a {alerta_def.num_condicao}{parametro.unidade}"
                else:  # 'maior_que'
                    titulo = f"{parametro.nome} maior que {alerta_def.num_condicao}{parametro.unidade}"

                # --- e colocamos a mensagem longa em descricaoAlerta ---
                descricao = alerta_def.mensagem

                novo_alerta = Alerta(
                    alerta_definido_id=alerta_def.id,
                    titulo=titulo,
                    data_hora=medida.data_hora,
                    valor_medido=medida.valor,
                    descricaoAlerta=descricao,
                    estacao=estacao.nome,
                    coordenadas=f"[{estacao.latitude},{estacao.longitude}]",
                    tempoFim=None
                )
                db.add(novo_alerta)

        else:
            # fecha todos os ativos
            for a in alertas_ativos:
                a.tempoFim = medida.data_hora

    await db.commit()

@router.post("/", response_model=MedidaResponse)
async def create_medida(medida: MedidaCreate, db: AsyncSession = Depends(get_async_db)):
    try:
        result = await db.execute(
            db.query(Estacao).filter(Estacao.id == medida.estacao_id)
        )
        estacao = result.scalar_one_or_none()
        if not estacao:
            raise HTTPException(status_code=404, detail="Estação não encontrada")

        result = await db.execute(
            db.query(Parametro).filter(Parametro.id == medida.parametro_id)
        )
        parametro = result.scalar_one_or_none()
        if not parametro:
            raise HTTPException(status_code=404, detail="Parâmetro não encontrado")

        db_medida = Medida(
            estacao_id=medida.estacao_id,
            parametro_id=medida.parametro_id,
            valor=medida.valor,
            data_hora=medida.data_hora or datetime.now()
        )
        db.add(db_medida)

        await check_and_create_alertas(db, db_medida, estacao, parametro)

        # commit final já feito dentro de check_and_create_alertas()
        await db.refresh(db_medida)
        return db_medida

    except Exception as e:
        await db.rollback()
        # aqui é impressa a stack trace completa no console
        logger.exception("Erro ao criar medida/alerta")
        # mantém o HTTP 500 para o cliente, mas com mensagem genérica
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# ... (restante das suas rotas GET, PUT, DELETE para Medida) ...

# Certifique-se de que as rotas GET, PUT, DELETE não precisam dessa lógica
# (elas operam em medidas existentes, não criam novas que poderiam disparar alertas)

@router.get("/", response_model=List[MedidaResponse])
async def read_medidas(db: AsyncSession = Depends(get_async_db)):
    try:
        result = await db.execute(db.query(Medida))
        medidas = result.scalars().all()
        return medidas
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{medida_id}", response_model=MedidaResponse)
async def read_medida(medida_id: int, db: AsyncSession = Depends(get_async_db)):
    try:
        result = await db.execute(
            db.query(Medida).filter(Medida.id == medida_id)
        )
        medida = result.scalar_one_or_none()
        if not medida:
            raise HTTPException(status_code=404, detail="Medida não encontrada")
        return medida
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{medida_id}", response_model=MedidaResponse)
async def update_medida(medida_id: int, medida: MedidaUpdate, db: AsyncSession = Depends(get_async_db)):
    try:
        result = await db.execute(
            db.query(Medida).filter(Medida.id == medida_id)
        )
        db_medida = result.scalar_one_or_none()
        if not db_medida:
            raise HTTPException(status_code=404, detail="Medida não encontrada")

        # Se estação_id foi fornecido, verifica se existe
        if medida.estacao_id is not None:
            result = await db.execute(
                db.query(Estacao).filter(Estacao.id == medida.estacao_id)
            )
            estacao = result.scalar_one_or_none()
            if not estacao:
                raise HTTPException(status_code=404, detail="Estação não encontrada")

        # Se parametro_id foi fornecido, verifica se existe
        if medida.parametro_id is not None:
            result = await db.execute(
                db.query(Parametro).filter(Parametro.id == medida.parametro_id)
            )
            parametro = result.scalar_one_or_none()
            if not parametro:
                raise HTTPException(status_code=404, detail="Parâmetro não encontrado")

        # Atualiza os campos da medida
        update_data = medida.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_medida, key, value)

        # **Nota**: Atualizar uma medida geralmente NÃO dispara novos alertas.
        # Se você precisar dessa lógica (o que é incomum), você teria que
        # chamar check_and_create_alertas aqui também, após atualizar o valor.

        await db.commit()
        await db.refresh(db_medida)
        return db_medida

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/lote", response_model=List[MedidaResponse])
async def create_medidas_lote(
    medidas: List[MedidaCreate] = Body(...),
    db: AsyncSession = Depends(get_async_db)
):
    criadas = []
    for medida in medidas:
        result = await db.execute(
            db.query(Estacao).filter(Estacao.id == medida.estacao_id)
        )
        estacao = result.scalar_one_or_none()
        if not estacao:
            raise HTTPException(status_code=404, detail="Estação não encontrada")

        result = await db.execute(
            db.query(Parametro).filter(Parametro.id == medida.parametro_id)
        )
        parametro = result.scalar_one_or_none()
        if not parametro:
            raise HTTPException(status_code=404, detail="Parâmetro não encontrado")

        db_medida = Medida(
            estacao_id=medida.estacao_id,
            parametro_id=medida.parametro_id,
            valor=medida.valor,
            data_hora=medida.data_hora or datetime.now()
        )
        db.add(db_medida)
        await db.flush()

        await check_and_create_alertas(db, db_medida, estacao, parametro)
        criadas.append(db_medida)

    await db.commit()
    return criadas

@router.delete("/{medida_id}", status_code=204)
async def delete_medida(medida_id: int, db: AsyncSession = Depends(get_async_db)):
    try:
        result = await db.execute(
            db.query(Medida).filter(Medida.id == medida_id)
        )
        db_medida = result.scalar_one_or_none()
        if not db_medida:
            raise HTTPException(status_code=404, detail="Medida não encontrada")

        # **Nota**: Deletar uma medida também geralmente NÃO afeta alertas existentes.
        # Alertas são registros históricos de quando uma condição FOI violada.

        await db.delete(db_medida)
        await db.commit()
        return None # Retorno padrão para 204 No Content
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))