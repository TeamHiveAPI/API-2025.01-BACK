from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from database import get_db
from models import TipoParametro
from schemas.tipo_parametro import (
    TipoParametroCreate, 
    TipoParametroResponse, 
    TipoParametroUpdate,
)
from core.security import get_current_user
from models import Usuario as UsuarioModel
from typing import List

router = APIRouter(prefix="/tipo_parametros", tags=["tipo parâmetros"])

@router.post("/", response_model=int, status_code=status.HTTP_201_CREATED)
async def create_tipo_parametro(
    tipo_parametro: TipoParametroCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user),
) -> int:
    try:
        new_tipo_parametro = TipoParametro(**tipo_parametro.dict())
        result = await db.execute(select(TipoParametro).where(TipoParametro.nome == new_tipo_parametro.nome))
        db_tipo_parametro = result.scalar_one_or_none()
        if db_tipo_parametro:
            raise HTTPException(status_code=400, detail="Tipo de parâmetro já existe.")
        db.add(new_tipo_parametro)
        await db.commit()
        await db.refresh(new_tipo_parametro)
        return new_tipo_parametro.id
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", response_model=List[TipoParametroResponse])
async def list_all_tipo_parametros(
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user),
) -> List[TipoParametroResponse]:
    tipo_parametros = []
    try:
        result = await db.execute(select(TipoParametro))
        db_tipo_parametros = result.scalars().all()
        for db_tipo_parametro in db_tipo_parametros:
            tipo_parametros.append(TipoParametroResponse.from_orm(db_tipo_parametro))
        return tipo_parametros
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{tipo_parametro_id}", response_model=TipoParametroResponse)
async def get_tipo_parametro_by_id(
    tipo_parametro_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user),
) -> TipoParametroResponse:
    try:
        result = await db.execute(select(TipoParametro).where(TipoParametro.id == tipo_parametro_id))
        db_tipo_parametro = result.scalar_one_or_none()
        if not db_tipo_parametro:
            raise HTTPException(status_code=404, detail="Tipo de parâmetro não encontrado.")
        return TipoParametroResponse.from_orm(db_tipo_parametro)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/{tipo_parametro_id}", response_model=dict)
async def update_tipo_parametro(
    tipo_parametro_id: int, 
    tipo_parametro: TipoParametroUpdate, 
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user),
) -> dict:
    try:
        result = await db.execute(select(TipoParametro).where(TipoParametro.id == tipo_parametro_id))
        db_tipo_parametro = result.scalar_one_or_none()
        if not db_tipo_parametro:
            raise HTTPException(status_code=404, detail="Tipo de parâmetro não encontrado.")
        
        if tipo_parametro.nome is not None:
            result_by_nome = await db.execute(select(TipoParametro).where(TipoParametro.nome == tipo_parametro.nome))
            db_tipo_parametro_by_nome = result_by_nome.scalar_one_or_none()
            if db_tipo_parametro_by_nome and db_tipo_parametro_by_nome.id != tipo_parametro_id:
                raise HTTPException(status_code=400, detail="Tipo de parâmetro já existe com este nome.")

        for field, value in tipo_parametro.dict(exclude_unset=True).items():
            setattr(db_tipo_parametro, field, value)
        await db.commit()
        await db.refresh(db_tipo_parametro)
        return {"message": "Tipo de parâmetro atualizado com sucesso"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{tipo_parametro_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def delete_tipo_parametro(
    tipo_parametro_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user),
) -> dict:
    try:
        result = await db.execute(select(TipoParametro).where(TipoParametro.id == tipo_parametro_id))
        db_tipo_parametro = result.scalar_one_or_none()
        if not db_tipo_parametro:
            raise HTTPException(status_code=404, detail="Tipo de parâmetro não encontrado.")
        
        await db.delete(db_tipo_parametro)
        await db.commit()
        return {"message": "Tipo de parâmetro deletado com sucesso"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))