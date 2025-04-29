from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Estacao, EstacaoParametro, Parametro
from schemas.estacao import EstacaoCreate, EstacaoResponse, EstacaoUpdate
from typing import List
from core.security import get_current_user
from models import Usuario as UsuarioModel

router = APIRouter(prefix="/estacoes", tags=["estações"])

@router.post("/", response_model=EstacaoResponse)
def create_estacao(
    estacao: EstacaoCreate, 
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user),
):
    try:
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
        return EstacaoResponse(
            id=db_estacao.id,
            uid=db_estacao.uid,
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
            sensores=[
                {
                    "id": sensor.id,
                    "nome": sensor.nome,
                    "unidade": sensor.unidade
                }
                for sensor in db_estacao.parametros
            ]
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{estacao_id}", response_model=EstacaoResponse)
def update_estacao(
    estacao_id: int, 
    estacao: EstacaoUpdate, 
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user),
):
    try:
        db_estacao = db.query(Estacao).filter(Estacao.id == estacao_id).first()
        if not db_estacao:
            raise HTTPException(status_code=404, detail="Estação não encontrada")

        # Atualiza os campos básicos da estação
        for key, value in estacao.dict(exclude={"sensores"}, exclude_unset=True).items():
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
        return EstacaoResponse(
            id=db_estacao.id,
            uid=db_estacao.uid,
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
            sensores=[
                {
                    "id": sensor.id,
                    "nome": sensor.nome,
                    "unidade": sensor.unidade
                }
                for sensor in db_estacao.parametros
            ]
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[EstacaoResponse])
def read_estacoes(db: Session = Depends(get_db)):
    try:
        estacoes = db.query(Estacao).all()
        estacoes_response = []
        for estacao in estacoes:
            estacao_data = EstacaoResponse(
                id=estacao.id,
                uid=estacao.uid,
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
                sensores=[
                    {
                        "id": sensor.id,
                        "nome": sensor.nome,
                        "unidade": sensor.unidade
                    }
                    for sensor in estacao.parametros
                ]
            )
            estacoes_response.append(estacao_data)
        return estacoes_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{estacao_id}", status_code=204)
def delete_estacao(
    estacao_id: int, 
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user),
):
    try:
        db_estacao = db.query(Estacao).filter(Estacao.id == estacao_id).first()
        if not db_estacao:
            raise HTTPException(status_code=404, detail="Estação não encontrada")
        # Remove as associações na tabela de ligação
        db.query(EstacaoParametro).filter(EstacaoParametro.estacao_id == estacao_id).delete()
        db.delete(db_estacao)
        db.commit()
        return None
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/uid/{uid}", response_model=EstacaoResponse)
def read_estacao_by_uid(uid: str, db: Session = Depends(get_db)):
    try:
        estacao = db.query(Estacao).filter(Estacao.uid == uid).first()
        if not estacao:
            raise HTTPException(status_code=404, detail="Estação não encontrada")
        
        return EstacaoResponse(
            id=estacao.id,
            uid=estacao.uid,
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
            sensores=[
                {
                    "id": sensor.id,
                    "nome": sensor.nome,
                    "unidade": sensor.unidade
                }
                for sensor in estacao.parametros
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))