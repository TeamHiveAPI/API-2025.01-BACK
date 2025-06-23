from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_async_db
from models import AlertaDefinido, Estacao, Parametro, Usuario, Alerta
import spacy

router = APIRouter()

nlp = spacy.load("pt_core_news_sm")

def interpretar_entrada(query: str):
    doc = nlp(query.lower())

    tipos = {
        "estacao": ["est", "estação", "estacao", "estacoes", "estações"],
        "sensor": ["sen", "par," "sensor", "sensores", "parametro", "parametros", "parametro", "parametros"],
        "alerta_definido": ["def," "adef", "alerta definido", "alertas definidos"],
        "usuario": ["usu", "usuario", "usuários", "usuarios"],
        "tipo_sensor": ["ts", "tipo", "tipo sensor", "tipo de sensor"]
    }

    tipo_detectado = None
    for token in doc:
        for tipo, palavras in tipos.items():
            if token.text in palavras:
                tipo_detectado = tipo
                break
        if tipo_detectado:
            break

    # Remove palavras-chave da consulta
    filtro = " ".join([token.text for token in doc if token.text not in sum(tipos.values(), [])])
    return {"tipo": tipo_detectado or "multiplo", "filtro": filtro.strip()}


async def buscar_estacoes_por_nome(db: AsyncSession, termo: str):
    result = await db.execute(select(Estacao).filter(Estacao.nome.ilike(f"%{termo}%")))
    return result.scalars().all()

async def buscar_sensores_por_nome(db: AsyncSession, termo: str):
    result = await db.execute(select(Parametro).filter(Parametro.nome.ilike(f"%{termo}%")))
    return result.scalars().all()

async def buscar_usuarios_por_nome(db: AsyncSession, termo: str):
    result = await db.execute(select(Usuario).filter(Usuario.nome.ilike(f"%{termo}%")))
    return result.scalars().all()

async def buscar_alertas_por_titulo(db: AsyncSession, termo: str):
    termo = termo.lower()

    result = await db.execute(select(AlertaDefinido))
    alertas = result.scalars().all()

    result = await db.execute(select(Parametro))
    parametros_map = {
        p.id: p for p in result.scalars().all()
    }

    result = await db.execute(select(Estacao))
    estacoes_map = {
        e.id: e for e in result.scalars().all()
    }

    resultados = []

    for alerta in alertas:
        parametro = parametros_map.get(alerta.parametro_id)
        estacao = estacoes_map.get(alerta.estacao_id)

        if not parametro or not estacao:
            continue

        cond = "maior ou igual a" if alerta.condicao == "maior_igual" else "menor que"
        unidade = parametro.unidade or ""
        titulo_virtual = f"{parametro.nome} {cond} {alerta.num_condicao}{unidade}".lower()

        if termo in titulo_virtual or termo in (alerta.mensagem or "").lower():
            resultados.append({
                "id": alerta.id,
                "estacao": estacao.nome,
                "estacao_id": estacao.id,
                "sensor": parametro.nome,
                "sensor_id": parametro.id,
                "unidade": unidade,
                "condicao": alerta.condicao,
                "num_condicao": alerta.num_condicao,
                "mensagem": alerta.mensagem,
            })

    return resultados


@router.get("/pesquisa")
async def pesquisa(query: str = Query(...), db: AsyncSession = Depends(get_async_db)):
    resultado = interpretar_entrada(query)
    tipo = resultado["tipo"]
    filtro = resultado["filtro"]

    if not filtro:
        return {
            "tipo": tipo,
            "resultados": {},
            "mensagem": "Nenhum critério de busca fornecido."
        }

    if tipo == "estacao":
        dados = await buscar_estacoes_por_nome(db, filtro)
        return {"tipo": tipo, "resultados": dados}
    elif tipo == "sensor":
        dados = await buscar_sensores_por_nome(db, filtro)
        return {"tipo": tipo, "resultados": dados}
    elif tipo == "usuario":
        dados = await buscar_usuarios_por_nome(db, filtro)
        return {"tipo": tipo, "resultados": dados}
    elif tipo == "alerta_definido":
        dados = await buscar_alertas_por_titulo(db, filtro)
        return {"tipo": tipo, "resultados": dados}

    resultados_multiplo = {
        "estacao": await buscar_estacoes_por_nome(db, filtro),
        "sensor": await buscar_sensores_por_nome(db, filtro),
        "usuario": await buscar_usuarios_por_nome(db, filtro),
        "alerta_definido": await buscar_alertas_por_titulo(db, filtro)
    }

    return {
        "tipo": "multiplo",
        "resultados": resultados_multiplo
    }