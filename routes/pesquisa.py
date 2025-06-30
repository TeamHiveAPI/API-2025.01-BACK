from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models import AlertaDefinido, Estacao, Parametro, Usuario, Alerta
import spacy
import logging
import json
from sqlalchemy.orm import joinedload

router = APIRouter(prefix="/pesquisa", tags=["pesquisa"])

logger = logging.getLogger("pesquisa")
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(logging.INFO)

try:
    nlp = spacy.load("pt_core_news_sm")
except OSError:
    from spacy.cli import download
    logger.warning("Modelo 'pt_core_news_sm' do spaCy não encontrado. Tentando baixar...")
    try:
        download("pt_core_news_sm")
        nlp = spacy.load("pt_core_news_sm")
        logger.info("Modelo 'pt_core_news_sm' do spaCy baixado e carregado com sucesso.")
    except Exception as e:
        logger.critical(f"Falha ao baixar e carregar o modelo 'pt_core_news_sm' do spaCy: {e}")
        nlp = None

def interpretar_entrada(query: str):
    if nlp is None:
        logger.warning("spaCy não carregado. Interpretação de entrada limitada.")
        query_lower = query.lower()
        if "estacao" in query_lower or "estação" in query_lower:
            return {"tipo": "estacao", "filtro": query_lower.replace("estacao", "").replace("estação", "").strip()}
        elif "sensor" in query_lower or "parametro" in query_lower:
            return {"tipo": "sensor", "filtro": query_lower.replace("sensor", "").replace("parametro", "").strip()}
        elif "usuario" in query_lower:
            return {"tipo": "usuario", "filtro": query_lower.replace("usuario", "").strip()}
        elif "alerta" in query_lower:
            return {"tipo": "alerta_definido", "filtro": query_lower.replace("alerta", "").strip()}
        return {"tipo": "multiplo", "filtro": query_lower.strip()}


    doc = nlp(query.lower())

    tipos = {
        "estacao": ["est", "estação", "estacao", "estacoes", "estações"],
        "sensor": ["sen", "par", "sensor", "sensores", "parametro", "parametros"],
        "alerta_definido": ["def", "adef", "alerta definido", "alertas definidos", "alerta", "alertas"],
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

    all_keywords = set(word for sublist in tipos.values() for word in sublist)
    filtro = " ".join([token.text for token in doc if token.text not in all_keywords])
    return {"tipo": tipo_detectado or "multiplo", "filtro": filtro.strip()}

async def buscar_estacoes_por_nome(db: AsyncSession, termo: str):
    result = await db.execute(select(Estacao).where(Estacao.nome.ilike(f"%{termo}%")))
    return result.scalars().all()

async def buscar_sensores_por_nome(db: AsyncSession, termo: str):
    result = await db.execute(select(Parametro).where(Parametro.nome.ilike(f"%{termo}%")))
    return result.scalars().all()

async def buscar_usuarios_por_nome(db: AsyncSession, termo: str):
    result = await db.execute(select(Usuario).where(Usuario.nome.ilike(f"%{termo}%")))
    return result.scalars().all()

async def buscar_alertas_por_titulo(db: AsyncSession, termo: str):
    termo = termo.lower()

    stmt = select(AlertaDefinido).options(
        joinedload(AlertaDefinido.parametro_rel), 
        joinedload(AlertaDefinido.estacao_rel)
    )
    result = await db.execute(stmt)
    alertas_definidos = result.scalars().all()

    resultados = []

    for alerta_def in alertas_definidos:
        parametro = alerta_def.parametro_rel 
        estacao = alerta_def.estacao_rel   

        if not parametro or not estacao:
            logger.warning(f"AlertaDefinido {alerta_def.id} com parâmetro ou estação ausente.")
            continue

        cond = "maior ou igual a" if alerta_def.condicao == "maior_igual" else ("menor que" if alerta_def.condicao == "menor" else "maior que")
        unidade = parametro.unidade or ""
        titulo_virtual = f"{parametro.nome} {cond} {alerta_def.num_condicao}{unidade}".lower()

        if termo in titulo_virtual or termo in (alerta_def.mensagem or "").lower():
            resultados.append({
                "id": alerta_def.id,
                "estacao": estacao.nome,
                "estacao_id": estacao.id,
                "sensor": parametro.nome,
                "sensor_id": parametro.id,
                "unidade": unidade,
                "condicao": alerta_def.condicao,
                "num_condicao": alerta_def.num_condicao,
                "mensagem": alerta_def.mensagem,
            })

    return resultados


@router.get("/")
async def pesquisa(query: str = Query(...), db: AsyncSession = Depends(get_db)):
    try:
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
    except Exception as e:
        logger.exception("Erro na rota de pesquisa")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno do servidor durante a pesquisa: {str(e)}")