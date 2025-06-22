from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_db
from models import Parametro, Estacao, EstacaoParametro
from schemas.parametro import ParametroCreate, ParametroResponse, ParametroUpdate
from typing import List
from core.security import get_current_user
from models import Usuario as UsuarioModel

router = APIRouter(prefix="/parametros", tags=["parâmetros"])

@router.post("/", response_model=int)
async def create_parametro(
    parametro: ParametroCreate, 
    db: AsyncSession = Depends(get_async_db),
    current_user: UsuarioModel = Depends(get_current_user),
) -> int:
    try:
        new_parametro = Parametro(**parametro.dict())
        result = await db.execute(
            db.query(Parametro).filter(Parametro.nome == new_parametro.nome)
        )
        db_parametro = result.scalar_one_or_none()
        if db_parametro:
            raise HTTPException(status_code=400, detail="Parâmetro já existe.")
        db.add(new_parametro)
        await db.commit()
        await db.refresh(new_parametro)
        return new_parametro.id
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[ParametroResponse])
async def list_all_parametros(
    db: AsyncSession = Depends(get_async_db),
) -> List[ParametroResponse]:
    try:
        result = await db.execute(db.query(Parametro))
        db_parametros = result.scalars().all()
        if not db_parametros:
            return []
        parametros = []
        for db_parametro in db_parametros:
            result = await db.execute(
                db.query(EstacaoParametro).filter(EstacaoParametro.parametro_id == db_parametro.id)
            )
            estacao_parametro = result.scalar_one_or_none()
            estacao_nome = None
            if estacao_parametro:
                result = await db.execute(
                    db.query(Estacao).filter(Estacao.id == estacao_parametro.estacao_id)
                )
                estacao = result.scalar_one_or_none()
                if estacao:
                    estacao_nome = estacao.nome
            parametro = ParametroResponse(
                **db_parametro.__dict__,
                estacao_nome=estacao_nome
            )
            parametros.append(parametro)
        return parametros
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{parametro_id}", response_model=ParametroResponse)
async def get_parametro_by_id(
    parametro_id: int, 
    db: AsyncSession = Depends(get_async_db),
    current_user: UsuarioModel = Depends(get_current_user),
) -> ParametroResponse:
    try:
        result = await db.execute(
            db.query(Parametro).filter(Parametro.id == parametro_id)
        )
        db_parametro = result.scalar_one_or_none()
        if not db_parametro:
            raise HTTPException(status_code=404, detail="Parâmetro não encontrado.")
        
        # Busca o nome da estação
        result = await db.execute(
            db.query(EstacaoParametro).filter(EstacaoParametro.parametro_id == db_parametro.id)
        )
        estacao_parametro = result.scalar_one_or_none()
        estacao_nome = None
        if estacao_parametro:
            result = await db.execute(
                db.query(Estacao).filter(Estacao.id == estacao_parametro.estacao_id)
            )
            estacao = result.scalar_one_or_none()
            if estacao:
                estacao_nome = estacao.nome

        return ParametroResponse(
            **db_parametro.__dict__,
            estacao_nome=estacao_nome
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{parametro_id}", response_model=dict)
async def update_parametro(
    parametro_id: int, 
    parametro: ParametroUpdate, 
    db: AsyncSession = Depends(get_async_db),
    current_user: UsuarioModel = Depends(get_current_user),
) -> dict:
    try:
        result = await db.execute(
            db.query(Parametro).filter(Parametro.id == parametro_id)
        )
        db_parametro = result.scalar_one_or_none()
        if not db_parametro:
            raise HTTPException(status_code=404, detail="Parâmetro não encontrado.")
        
        if parametro.nome is not None:
            result = await db.execute(
                db.query(Parametro).filter(Parametro.nome == parametro.nome)
            )
            db_parametro_by_nome = result.scalar_one_or_none()
            if db_parametro_by_nome and db_parametro_by_nome.id != parametro_id:
                raise HTTPException(status_code=400, detail="Parâmetro já existe com este nome.")

        for field, value in parametro.dict(exclude_unset=True).items():
            setattr(db_parametro, field, value)
        await db.commit()
        return {"message": "Parâmetro atualizado com sucesso"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{parametro_id}", response_model=dict)
async def delete_parametro(
    parametro_id: int, 
    db: AsyncSession = Depends(get_async_db),
    current_user: UsuarioModel = Depends(get_current_user),
) -> dict:
    try:
        result = await db.execute(
            db.query(Parametro).filter(Parametro.id == parametro_id)
        )
        db_parametro = result.scalar_one_or_none()
        if not db_parametro:
            raise HTTPException(status_code=404, detail="Parâmetro não encontrado.")
        await db.delete(db_parametro)
        await db.commit()
        return {"message": "Parâmetro deletado com sucesso"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))