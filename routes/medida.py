# routers/medida.py
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
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

def check_and_create_alertas(db: Session, medida: Medida, estacao: Estacao, parametro: Parametro):
    alertas_definidos = db.query(AlertaDefinido).filter(
        AlertaDefinido.estacao_id == medida.estacao_id,
        AlertaDefinido.parametro_id == medida.parametro_id
    ).all()

    for alerta_def in alertas_definidos:
        alertas_ativos = db.query(Alerta).filter(
            Alerta.alerta_definido_id == alerta_def.id,
            Alerta.tempoFim.is_(None)
        ).all()

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

    db.commit()

@router.post("/", response_model=MedidaResponse)
def create_medida(medida: MedidaCreate, db: Session = Depends(get_db)):
    try:
        estacao = db.query(Estacao).filter(Estacao.id == medida.estacao_id).first()
        if not estacao:
            raise HTTPException(status_code=404, detail="Estação não encontrada")

        parametro = db.query(Parametro).filter(Parametro.id == medida.parametro_id).first()
        if not parametro:
            raise HTTPException(status_code=404, detail="Parâmetro não encontrado")

        db_medida = Medida(
            estacao_id=medida.estacao_id,
            parametro_id=medida.parametro_id,
            valor=medida.valor,
            data_hora=medida.data_hora or datetime.now()
        )
        db.add(db_medida)

        check_and_create_alertas(db, db_medida, estacao, parametro)

        # commit final já feito dentro de check_and_create_alertas()
        db.refresh(db_medida)
        return db_medida

    except Exception as e:
        db.rollback()
        # aqui é impressa a stack trace completa no console
        logger.exception("Erro ao criar medida/alerta")
        # mantém o HTTP 500 para o cliente, mas com mensagem genérica
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# ... (restante das suas rotas GET, PUT, DELETE para Medida) ...

# Certifique-se de que as rotas GET, PUT, DELETE não precisam dessa lógica
# (elas operam em medidas existentes, não criam novas que poderiam disparar alertas)

@router.get("/", response_model=List[MedidaResponse])
def read_medidas(db: Session = Depends(get_db)):
    try:
        medidas = db.query(Medida).all()
        return medidas
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{medida_id}", response_model=MedidaResponse)
def read_medida(medida_id: int, db: Session = Depends(get_db)):
    try:
        medida = db.query(Medida).filter(Medida.id == medida_id).first()
        if not medida:
            raise HTTPException(status_code=404, detail="Medida não encontrada")
        return medida
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{medida_id}", response_model=MedidaResponse)
def update_medida(medida_id: int, medida: MedidaUpdate, db: Session = Depends(get_db)):
    try:
        db_medida = db.query(Medida).filter(Medida.id == medida_id).first()
        if not db_medida:
            raise HTTPException(status_code=404, detail="Medida não encontrada")

        # Se estação_id foi fornecido, verifica se existe
        if medida.estacao_id is not None:
            estacao = db.query(Estacao).filter(Estacao.id == medida.estacao_id).first()
            if not estacao:
                raise HTTPException(status_code=404, detail="Estação não encontrada")

        # Se parametro_id foi fornecido, verifica se existe
        if medida.parametro_id is not None:
            parametro = db.query(Parametro).filter(Parametro.id == medida.parametro_id).first()
            if not parametro:
                raise HTTPException(status_code=404, detail="Parâmetro não encontrado")

        # Atualiza os campos da medida
        update_data = medida.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_medida, key, value)

        # **Nota**: Atualizar uma medida geralmente NÃO dispara novos alertas.
        # Se você precisar dessa lógica (o que é incomum), você teria que
        # chamar check_and_create_alertas aqui também, após atualizar o valor.

        db.commit()
        db.refresh(db_medida)
        return db_medida

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{medida_id}", status_code=204)
def delete_medida(medida_id: int, db: Session = Depends(get_db)):
    try:
        db_medida = db.query(Medida).filter(Medida.id == medida_id).first()
        if not db_medida:
            raise HTTPException(status_code=404, detail="Medida não encontrada")

        # **Nota**: Deletar uma medida também geralmente NÃO afeta alertas existentes.
        # Alertas são registros históricos de quando uma condição FOI violada.

        db.delete(db_medida)
        db.commit()
        return None # Retorno padrão para 204 No Content
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))