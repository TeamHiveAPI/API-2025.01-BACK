from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Estacao, EstacaoParametro, Parametro
from schemas.estacao import EstacaoCreate, EstacaoResponse
from typing import List

router = APIRouter(prefix="/estacoes", tags=["estações"])

@router.post("/", response_model=EstacaoResponse)
def create_estacao(estacao: EstacaoCreate, db: Session = Depends(get_db)):
    # Cria a estação
    db_estacao = Estacao(
        nome=estacao.nome,
        cep=estacao.cep,
        rua=estacao.rua,
        bairro=estacao.bairro,
        cidade=estacao.cidade,
        numero=estacao.numero,
        latitude=estacao.latitude,
        longitude=estacao.longitude,
        data_instalacao=estacao.data_instalacao,
        status=estacao.status,
    )
    db.add(db_estacao)
    db.commit()
    db.refresh(db_estacao)

    # Insere os sensores na tabela associativa, se fornecidos
    if estacao.sensores:
        for sensor_id in estacao.sensores:
            sensor = db.query(Parametro).filter(Parametro.id == sensor_id).first()
            if sensor is None:
                raise HTTPException(status_code=404, detail=f"Sensor (parâmetro) com ID {sensor_id} não encontrado.")
            assoc = EstacaoParametro(estacao_id=db_estacao.id, parametro_id=sensor_id)
            db.add(assoc)
        db.commit()

    # Inclui os IDs dos sensores na resposta
    sensores_ids = [sensor_id for sensor_id in estacao.sensores] if estacao.sensores else []
    return EstacaoResponse(
        id=db_estacao.id,
        nome=db_estacao.nome,
        cep=db_estacao.cep,
        rua=db_estacao.rua,
        bairro=db_estacao.bairro,
        cidade=db_estacao.cidade,
        numero=db_estacao.numero,
        latitude=db_estacao.latitude,
        longitude=db_estacao.longitude,
        data_instalacao=db_estacao.data_instalacao,
        status=db_estacao.status,
        sensores=sensores_ids
    )

@router.put("/{estacao_id}", response_model=EstacaoResponse)
def update_estacao(estacao_id: int, estacao: EstacaoCreate, db: Session = Depends(get_db)):
    db_estacao = db.query(Estacao).filter(Estacao.id == estacao_id).first()
    if not db_estacao:
        raise HTTPException(status_code=404, detail="Estação não encontrada")

    # Atualiza os campos básicos da estação
    for key, value in estacao.dict(exclude={"sensores"}).items():
        setattr(db_estacao, key, value)
    db.commit()

    # Remove as associações atuais de sensores
    db.query(EstacaoParametro).filter(EstacaoParametro.estacao_id == estacao_id).delete()
    db.commit()

    # Adiciona as novas associações de sensores
    if estacao.sensores:
        for sensor_id in estacao.sensores:
            sensor = db.query(Parametro).filter(Parametro.id == sensor_id).first()
            if sensor is None:
                raise HTTPException(status_code=404, detail=f"Sensor (parâmetro) com ID {sensor_id} não encontrado.")
            assoc = EstacaoParametro(estacao_id=estacao_id, parametro_id=sensor_id)
            db.add(assoc)
        db.commit()

    db.refresh(db_estacao)
    # Inclui os IDs dos sensores na resposta
    sensores_ids = [parametro.id for parametro in db_estacao.parametros]
    return EstacaoResponse(
        id=db_estacao.id,
        nome=db_estacao.nome,
        cep=db_estacao.cep,
        rua=db_estacao.rua,
        bairro=db_estacao.bairro,
        cidade=db_estacao.cidade,
        numero=db_estacao.numero,
        latitude=db_estacao.latitude,
        longitude=db_estacao.longitude,
        data_instalacao=db_estacao.data_instalacao,
        status=db_estacao.status,
        sensores=sensores_ids
    )

@router.get("/", response_model=List[EstacaoResponse])
def read_estacoes(db: Session = Depends(get_db)):
    estacoes = db.query(Estacao).all()
    estacoes_response = []
    for estacao in estacoes:
        # Obtém os IDs dos sensores vinculados
        sensores_ids = [parametro.id for parametro in estacao.parametros]
        estacao_data = EstacaoResponse(
            id=estacao.id,
            nome=estacao.nome,
            cep=estacao.cep,
            rua=estacao.rua,
            bairro=estacao.bairro,
            cidade=estacao.cidade,
            numero=estacao.numero,
            latitude=estacao.latitude,
            longitude=estacao.longitude,
            data_instalacao=estacao.data_instalacao,
            status=estacao.status,
            sensores=sensores_ids
        )
        estacoes_response.append(estacao_data)
    return estacoes_response

@router.delete("/{estacao_id}", status_code=204)
def delete_estacao(estacao_id: int, db: Session = Depends(get_db)):
    db_estacao = db.query(Estacao).filter(Estacao.id == estacao_id).first()
    if not db_estacao:
        raise HTTPException(status_code=404, detail="Estação não encontrada")
    # Remove as associações na tabela de ligação
    db.query(EstacaoParametro).filter(EstacaoParametro.estacao_id == estacao_id).delete()
    db.delete(db_estacao)
    db.commit()
    return None