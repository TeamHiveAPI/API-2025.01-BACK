# routers/medida.py
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

def check_and_create_alertas(db: Session, medida: Medida, estacao: Estacao, parametro: Parametro):
    """
    Verifica se a medida aciona algum AlertaDefinido e cria Alertas se necessário.
    """
    # Busca alertas definidos para esta combinação de estação e parâmetro
    alertas_definidos = db.query(AlertaDefinido).filter(
        AlertaDefinido.estacao_id == medida.estacao_id,
        AlertaDefinido.parametro_id == medida.parametro_id
    ).all()

    for alerta_def in alertas_definidos:
        # Verifica se existe um alerta ativo para este alerta_definido
        alerta_ativo = db.query(Alerta).filter(
            Alerta.alerta_definido_id == alerta_def.id,
            Alerta.tempoFim == None
        ).first()

        triggered = False
        condicao_texto = ""

        if alerta_def.condicao == 'menor' and medida.valor < alerta_def.num_condicao:
            triggered = True
            condicao_texto = f"abaixo do limite de {alerta_def.num_condicao}{parametro.unidade}"
        elif alerta_def.condicao == 'maior_igual' and medida.valor >= alerta_def.num_condicao:
            triggered = True
            condicao_texto = f"igual ou acima do limite de {alerta_def.num_condicao}{parametro.unidade}"
        elif alerta_def.condicao == 'maior_que' and medida.valor > alerta_def.num_condicao:
            triggered = True
            condicao_texto = f"acima do limite de {alerta_def.num_condicao}{parametro.unidade}"

        # Se não está mais em condição de alerta e existe um alerta ativo, finaliza o alerta
        if not triggered and alerta_ativo:
            alerta_ativo.tempoFim = medida.data_hora
            db.commit()
            continue

        # Se está em condição de alerta e não existe alerta ativo, cria um novo
        if triggered and not alerta_ativo:
            titulo_alerta = getattr(alerta_def, 'nome_alerta', f"Alerta de {parametro.nome}")
            
            descricao = (f"{parametro.nome} registrou {medida.valor}{parametro.unidade} na estação '{estacao.nome}', "
                         f"que está {condicao_texto}.")

            coordenadas_str = f"[{estacao.latitude},{estacao.longitude}]"

            novo_alerta = Alerta(
                alerta_definido_id=alerta_def.id,
                titulo=titulo_alerta,
                data_hora=medida.data_hora,
                valor_medido=medida.valor,
                descricaoAlerta=descricao,
                estacao=estacao.nome,
                coordenadas=coordenadas_str,
                tempoFim=None
            )
            db.add(novo_alerta)
            # O commit será feito fora da função, após todas as verificações

@router.post("/", response_model=MedidaResponse)
def create_medida(medida: MedidaCreate, db: Session = Depends(get_db)):
    try:
        # Verifica se a estação existe
        estacao = db.query(Estacao).filter(Estacao.id == medida.estacao_id).first()
        if not estacao:
            raise HTTPException(status_code=404, detail="Estação não encontrada")

        # Verifica se o parâmetro existe
        parametro = db.query(Parametro).filter(Parametro.id == medida.parametro_id).first()
        if not parametro:
            raise HTTPException(status_code=404, detail="Parâmetro não encontrado")

        # **Importante**: Verifique se o sensor (parâmetro) está realmente associado a esta estação
        # Isso já deve estar garantido pelo seu front-end ou lógica de negócio,
        # mas uma verificação extra pode ser útil se necessário.
        # assoc = db.query(EstacaoParametro).filter(
        #     EstacaoParametro.estacao_id == medida.estacao_id,
        #     EstacaoParametro.parametro_id == medida.parametro_id
        # ).first()
        # if not assoc:
        #     raise HTTPException(status_code=400, detail="Sensor (parâmetro) não está associado a esta estação.")


        # Cria a medida
        db_medida = Medida(
            estacao_id=medida.estacao_id,
            parametro_id=medida.parametro_id,
            valor=medida.valor,
            # Garante que data_hora seja definida, use 'now' se não for fornecida
            data_hora=medida.data_hora if medida.data_hora else datetime.now()
        )
        db.add(db_medida)
        # Commit inicial para obter o ID da medida, se necessário, ou comitar tudo no final
        # É mais seguro fazer um commit único no final do bloco try.
        # db.commit()
        # db.refresh(db_medida)

        # ---> Início da Lógica de Verificação de Alertas <---
        # Chama a função para verificar e criar alertas ANTES do commit final
        check_and_create_alertas(db, db_medida, estacao, parametro)
        # ---> Fim da Lógica de Verificação de Alertas <---

        # Commit final para salvar a medida e quaisquer alertas criados
        db.commit()
        db.refresh(db_medida) # Refresh após o commit para obter estado atualizado

        return db_medida

    except Exception as e:
        db.rollback() # Garante que nem a medida nem os alertas sejam salvos em caso de erro
        # Log do erro pode ser útil aqui: print(f"Erro ao criar medida/alerta: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

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