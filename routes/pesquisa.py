from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models import AlertaDefinido, Estacao, Parametro, Usuario, Alerta
import spacy

router = APIRouter()

nlp = spacy.load("pt_core_news_sm")

def interpretar_entrada(query: str):
    doc = nlp(query.lower())

    tipos = {
        "estacao": ["estação", "estacao", "estacoes"],
        "sensor": ["sensor", "sensores", "parametro"],
        "alerta_definido": ["alerta definido", "alertas definidos"],
        "usuario": ["usuario", "usuários"],
        "tipo_sensor": ["tipo", "tipo sensor", "tipo de sensor"]
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


def buscar_estacoes_por_nome(db: Session, termo: str):
    return db.query(Estacao).filter(Estacao.nome.ilike(f"%{termo}%")).all()

def buscar_sensores_por_nome(db: Session, termo: str):
    return db.query(Parametro).filter(Parametro.nome.ilike(f"%{termo}%")).all()

def buscar_usuarios_por_nome(db: Session, termo: str):
    return db.query(Usuario).filter(Usuario.nome.ilike(f"%{termo}%")).all()

def buscar_alertas_por_titulo(db: Session, termo: str):
    termo = termo.lower()

    alertas = db.query(AlertaDefinido).all()

    parametros_map = {
        p.id: p for p in db.query(Parametro).all()
    }

    estacoes_map = {
        e.id: e for e in db.query(Estacao).all()
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
def pesquisa(query: str = Query(...), db: Session = Depends(get_db)):
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
        dados = buscar_estacoes_por_nome(db, filtro)
        return {"tipo": tipo, "resultados": dados}
    elif tipo == "sensor":
        dados = buscar_sensores_por_nome(db, filtro)
        return {"tipo": tipo, "resultados": dados}
    elif tipo == "usuario":
        dados = buscar_usuarios_por_nome(db, filtro)
        return {"tipo": tipo, "resultados": dados}
    elif tipo == "alerta_definido":
        dados = buscar_alertas_por_titulo(db, filtro)
        return {"tipo": tipo, "resultados": dados}

    resultados_multiplo = {
        "estacao": buscar_estacoes_por_nome(db, filtro),
        "sensor": buscar_sensores_por_nome(db, filtro),
        "usuario": buscar_usuarios_por_nome(db, filtro),
        "alerta_definido": buscar_alertas_por_titulo(db, filtro)
    }

    return {
        "tipo": "multiplo",
        "resultados": resultados_multiplo
    }