from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from database import get_db
from models import AlertaDefinido, Estacao, Parametro, EstacaoParametro
from schemas.alerta_definido import AlertaDefinidoCreate, AlertaDefinidoResponse, AlertaDefinidoUpdate
from core.security import get_current_user
from models import Usuario as UsuarioModel
from typing import List

router = APIRouter(prefix="/alertas-definidos", tags=["alertas definidos"])

@router.post("/", response_model=AlertaDefinidoResponse, status_code=status.HTTP_201_CREATED)
async def create_alerta_definido(
    alerta_definido: AlertaDefinidoCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user),
):
    try:
        result_estacao = await db.execute(select(Estacao).where(Estacao.id == alerta_definido.estacao_id))
        db_estacao = result_estacao.scalar_one_or_none()
        if not db_estacao:
            raise HTTPException(status_code=404, detail="Estação não encontrada")
        
        result_parametro = await db.execute(select(Parametro).where(Parametro.id == alerta_definido.parametro_id))
        db_parametro = result_parametro.scalar_one_or_none()
        if not db_parametro:
            raise HTTPException(status_code=404, detail="Sensor (parâmetro) não encontrado")

        result_link = await db.execute(
            select(EstacaoParametro).where(
                EstacaoParametro.estacao_id == alerta_definido.estacao_id,
                EstacaoParametro.parametro_id == alerta_definido.parametro_id
            )
        )
        db_link = result_link.scalar_one_or_none()
        if not db_link:
            raise HTTPException(status_code=400, detail="Sensor não vinculado à estação informada")

        db_alerta_definido = AlertaDefinido(**alerta_definido.dict())
        db.add(db_alerta_definido)
        await db.commit()
        await db.refresh(db_alerta_definido)
        return db_alerta_definido
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", response_model=List[AlertaDefinidoResponse])
async def list_alertas_definidos(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AlertaDefinido))
    return result.scalars().all()

@router.get("/{alerta_definido_id}", response_model=AlertaDefinidoResponse)
async def get_alerta_definido(alerta_definido_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AlertaDefinido).where(AlertaDefinido.id == alerta_definido_id))
    db_alerta_definido = result.scalar_one_or_none()
    if not db_alerta_definido:
        raise HTTPException(status_code=404, detail="Alerta definido não encontrado")
    return db_alerta_definido

@router.put("/{alerta_definido_id}", response_model=AlertaDefinidoResponse)
async def update_alerta_definido(
    alerta_definido_id: int, 
    alerta_definido: AlertaDefinidoUpdate, 
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user),
):
    try:
        result = await db.execute(select(AlertaDefinido).where(AlertaDefinido.id == alerta_definido_id))
        db_alerta_definido = result.scalar_one_or_none()
        if not db_alerta_definido:
            raise HTTPException(status_code=404, detail="Alerta definido não encontrado")
        
        estacao_id = alerta_definido.estacao_id if alerta_definido.estacao_id is not None else db_alerta_definido.estacao_id
        parametro_id = alerta_definido.param.id if alerta_definido.parametro_id is not None else db_alerta_definido.parametro_id

        result_estacao = await db.execute(select(Estacao).where(Estacao.id == estacao_id))
        db_estacao = result_estacao.scalar_one_or_none()
        if not db_estacao:
            raise HTTPException(status_code=404, detail="Estação não encontrada")

        result_parametro = await db.execute(select(Parametro).where(Parametro.id == parametro_id))
        db_parametro = result_parametro.scalar_one_or_none()
        if not db_parametro:
            raise HTTPException(status_code=404, detail="Sensor (parâmetro) não encontrado")

        result_link = await db.execute(
            select(EstacaoParametro).where(
                EstacaoParametro.estacao_id == estacao_id,
                EstacaoParametro.parametro_id == parametro_id
            )
        )
        db_link = result_link.scalar_one_or_none()
        if not db_link:
            raise HTTPException(status_code=400, detail="Sensor não vinculado à estação informada")
        
        for key, value in alerta_definido.dict(exclude_unset=True).items():
            setattr(db_alerta_definido, key, value)
        
        await db.commit()
        await db.refresh(db_alerta_definido)
        return db_alerta_definido
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{alerta_definido_id}", status_code=status.HTTP_200_OK)
async def delete_alerta_definido(
    alerta_definido_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user),
):
    try:
        result = await db.execute(select(AlertaDefinido).where(AlertaDefinido.id == alerta_definido_id))
        db_alerta_definido = result.scalar_one_or_none()
        if not db_alerta_definido:
            raise HTTPException(status_code=404, detail="Alerta definido não encontrado")
        
        await db.delete(db_alerta_definido)
        await db.commit()
        return {"message": "Alerta definido deletado com sucesso"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))