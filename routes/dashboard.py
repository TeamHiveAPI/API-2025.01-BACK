from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from database import get_db
from models import Estacao, Parametro, AlertaDefinido, Usuario

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/contagem-entidades", response_model=dict)
async def dashboard(db: AsyncSession = Depends(get_db)) -> dict:
    try:
        result_estacoes = await db.execute(select(func.count(Estacao.id)))
        num_estacoes = result_estacoes.scalar_one()

        result_sensores = await db.execute(select(func.count(Parametro.id)))
        num_sensores = result_sensores.scalar_one()

        result_alertas = await db.execute(select(func.count(AlertaDefinido.id)))
        num_alertas = result_alertas.scalar_one()

        result_usuarios = await db.execute(select(func.count(Usuario.id)))
        num_usuarios = result_usuarios.scalar_one()

        return {
            "numEstacoes": num_estacoes,
            "numSensores": num_sensores,
            "numAlertas": num_alertas,
            "numUsuarios": num_usuarios
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao processar requisição: {str(e)}")