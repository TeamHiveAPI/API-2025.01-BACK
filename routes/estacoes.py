from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.orm import selectinload
from database import get_db
from models import Estacao, EstacaoParametro, Parametro
from schemas.estacao import EstacaoCreate, EstacaoResponse, EstacaoUpdate
from typing import List
from core.security import get_current_user
from models import Usuario as UsuarioModel

router = APIRouter(prefix="/estacoes", tags=["estações"])

@router.post("/", response_model=EstacaoResponse, status_code=status.HTTP_201_CREATED)
async def create_estacao(
    estacao: EstacaoCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user),
):
    try:
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
        await db.commit()
        await db.refresh(db_estacao)

        if estacao.sensores:
            for sensor_id in estacao.sensores:
                result = await db.execute(select(Parametro).where(Parametro.id == sensor_id))
                sensor = result.scalar_one_or_none()
                if sensor is None:
                    raise HTTPException(status_code=404, detail=f"Sensor (parâmetro) com ID {sensor_id} não encontrado.")
                assoc = EstacaoParametro(estacao_id=db_estacao.id, parametro_id=sensor_id)
                db.add(assoc)
            await db.commit()
            
        # Recarregar a estação com os parâmetros
        result = await db.execute(
            select(Estacao).options(selectinload(Estacao.parametros)).where(Estacao.id == db_estacao.id)
        )
        db_estacao_with_params = result.scalar_one()
        
        return EstacaoResponse(
            id=db_estacao_with_params.id,
            uid=db_estacao_with_params.uid,
            nome=db_estacao_with_params.nome,
            cep=db_estacao_with_params.cep,
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
                for sensor in db_estacao_with_params.parametros
            ]
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/{estacao_id}", response_model=EstacaoResponse)
async def update_estacao(
    estacao_id: int, 
    estacao: EstacaoUpdate, 
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user),
):
    try:
        result = await db.execute(select(Estacao).where(Estacao.id == estacao_id))
        db_estacao = result.scalar_one_or_none()
        if not db_estacao:
            raise HTTPException(status_code=404, detail="Estação não encontrada")

        for key, value in estacao.dict(exclude={"sensores"}, exclude_unset=True).items():
            setattr(db_estacao, key, value)
        await db.commit()

        await db.execute(delete(EstacaoParametro).where(EstacaoParametro.estacao_id == estacao_id))
        await db.commit()

        if estacao.sensores:
            for sensor_id in estacao.sensores:
                result = await db.execute(select(Parametro).where(Parametro.id == sensor_id))
                sensor = result.scalar_one_or_none()
                if sensor is None:
                    raise HTTPException(status_code=404, detail=f"Sensor (parâmetro) com ID {sensor_id} não encontrado.")
                assoc = EstacaoParametro(estacao_id=estacao_id, parametro_id=sensor_id)
                db.add(assoc)
            await db.commit()

        # Recarregar a estação com os parâmetros
        result = await db.execute(
            select(Estacao).options(selectinload(Estacao.parametros)).where(Estacao.id == estacao_id)
        )
        db_estacao_with_params = result.scalar_one()
        
        return EstacaoResponse(
            id=db_estacao_with_params.id,
            uid=db_estacao_with_params.uid,
            nome=db_estacao_with_params.nome,
            cep=db_estacao_with_params.cep,
            rua=db_estacao_with_params.rua,
            bairro=db_estacao_with_params.bairro,
            cidade=db_estacao_with_params.cidade,
            numero=db_estacao_with_params.numero,
            latitude=db_estacao_with_params.latitude,
            longitude=db_estacao_with_params.longitude,
            data_instalacao=db_estacao_with_params.data_instalacao,
            status=db_estacao_with_params.status,
            sensores=[
                {
                    "id": sensor.id,
                    "nome": sensor.nome,
                    "unidade": sensor.unidade
                }
                for sensor in db_estacao_with_params.parametros
            ]
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", response_model=List[EstacaoResponse])
async def read_estacoes(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Estacao).options(selectinload(Estacao.parametros)))
        estacoes = result.scalars().all()
        
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{estacao_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_estacao(
    estacao_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user),
):
    try:
        result = await db.execute(select(Estacao).where(Estacao.id == estacao_id))
        db_estacao = result.scalar_one_or_none()
        if not db_estacao:
            raise HTTPException(status_code=404, detail="Estação não encontrada")
        
        await db.execute(delete(EstacaoParametro).where(EstacaoParametro.estacao_id == estacao_id))
        
        await db.delete(db_estacao)
        await db.commit()
        return None
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/uid/{uid}", response_model=EstacaoResponse)
async def read_estacao_by_uid(uid: str, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Estacao).options(selectinload(Estacao.parametros)).where(Estacao.uid == uid))
        estacao = result.scalar_one_or_none()
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))