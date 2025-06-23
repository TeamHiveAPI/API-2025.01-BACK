from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import get_async_db
from models import Estacao, Parametro, AlertaDefinido, Usuario

# Definição do roteador
router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/contagem-entidades", response_model=dict)
async def dashboard(db: AsyncSession = Depends(get_async_db)) -> dict:
    try:
        result = await db.execute(select(func.count()).select_from(Estacao))
        num_estacoes = result.scalar()

        result = await db.execute(select(func.count()).select_from(Parametro))
        num_sensores = result.scalar()

        result = await db.execute(select(func.count()).select_from(AlertaDefinido))
        num_alertas = result.scalar()

        result = await db.execute(select(func.count()).select_from(Usuario))
        num_usuarios = result.scalar()

        # Retorno das informações
        return {
            "numEstacoes": num_estacoes,
            "numSensores": num_sensores,
            "numAlertas": num_alertas,
            "numUsuarios": num_usuarios
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar requisição: {str(e)}")