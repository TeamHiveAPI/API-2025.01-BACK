from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from database import get_db
from models import Alerta
from typing import List
from schemas.alerta import AlertaCreate, AlertaResponse, AlertaUpdate
from core.security import get_current_user
from models import Usuario as UsuarioModel

router = APIRouter(prefix="/alertas", tags=["alertas"])

@router.post("/", response_model=AlertaResponse, status_code=status.HTTP_201_CREATED)
async def create_alerta(
    alerta: AlertaCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user),
):
    try:
        db_alerta = Alerta(**alerta.dict())
        db.add(db_alerta)
        await db.commit()
        await db.refresh(db_alerta)
        return db_alerta
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{alerta_id}", response_model=AlertaResponse)
async def get_alerta(alerta_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Alerta).where(Alerta.id == alerta_id))
    db_alerta = result.scalar_one_or_none()
    if not db_alerta:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    return db_alerta

@router.put("/{alerta_id}", response_model=AlertaResponse)
async def update_alerta(
    alerta_id: int, 
    alerta: AlertaUpdate, 
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user),
):
    try:
        result = await db.execute(select(Alerta).where(Alerta.id == alerta_id))
        db_alerta = result.scalar_one_or_none()
        if not db_alerta:
            raise HTTPException(status_code=404, detail="Alerta não encontrado")
        
        for key, value in alerta.dict(exclude_unset=True).items():
            setattr(db_alerta, key, value)
        
        await db.commit()
        await db.refresh(db_alerta)
        return db_alerta
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{alerta_id}", status_code=status.HTTP_200_OK)
async def delete_alerta(
    alerta_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user),
):
    try:
        result = await db.execute(select(Alerta).where(Alerta.id == alerta_id))
        db_alerta = result.scalar_one_or_none()
        if not db_alerta:
            raise HTTPException(status_code=404, detail="Alerta não encontrado")
        
        await db.delete(db_alerta)
        await db.commit()
        return {"message": "Alerta deletado com sucesso"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", response_model=List[AlertaResponse])
async def list_alertas(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Alerta))
    alertas = result.scalars().all()
    
    return [
        AlertaResponse(
            id=alerta.id,
            alerta_definido_id=alerta.alerta_definido_id,
            titulo=alerta.titulo,
            data_hora=alerta.data_hora,
            valor_medido=alerta.valor_medido,
            descricaoAlerta=alerta.descricaoAlerta,
            estacao=alerta.estacao,
            coordenadas=list(map(float, alerta.coordenadas.strip("[]").split(","))) if isinstance(alerta.coordenadas, str) else alerta.coordenadas,
            tempoFim=alerta.tempoFim,
            alertaAtivo=alerta.tempoFim is None,
            expandido=False
        )
        for alerta in alertas
    ]

@router.get("/passados", response_model=List[AlertaResponse])
async def list_alertas_passados(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Alerta).where(Alerta.tempoFim != None)
    )
    alertas_passados = result.scalars().all()

    return [
        AlertaResponse(
            id=alerta.id,
            alerta_definido_id=alerta.alerta_definido_id,
            alertaAtivo=False,
            titulo=alerta.titulo,
            data_hora=alerta.data_hora,
            valor_medido=alerta.valor_medido,
            descricaoAlerta=alerta.descricaoAlerta,
            estacao=alerta.estacao,
            coordenadas=eval(alerta.coordenadas) if isinstance(alerta.coordenadas, str) else alerta.coordenadas,
            tempoFim=alerta.tempoFim,
            expandido=False
        )
        for alerta in alertas_passados
    ]

@router.get("/mais-recente", response_model=AlertaResponse)
async def get_alerta_mais_recente(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Alerta).order_by(Alerta.data_hora.desc())
    )
    alerta = result.scalar_one_or_none()
    if not alerta:
        raise HTTPException(status_code=404, detail="Nenhum alerta encontrado")

    return AlertaResponse(
        id=alerta.id,
        alerta_definido_id=alerta.alerta_definido_id,
        alertaAtivo=alerta.tempoFim is None,
        titulo=alerta.titulo,
        data_hora=alerta.data_hora,
        valor_medido=alerta.valor_medido,
        descricaoAlerta=alerta.descricaoAlerta,
        estacao=alerta.estacao,
        coordenadas=eval(alerta.coordenadas) if isinstance(alerta.coordenadas, str) else alerta.coordenadas,
        tempoFim=alerta.tempoFim,
        expandido=False
    )