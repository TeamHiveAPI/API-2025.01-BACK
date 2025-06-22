# routers/alertas_definidos.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_db
from models import AlertaDefinido, Estacao, Parametro, EstacaoParametro
from schemas.alerta_definido import AlertaDefinidoCreate, AlertaDefinidoResponse, AlertaDefinidoUpdate
from core.security import get_current_user
from models import Usuario as UsuarioModel

router = APIRouter(prefix="/alertas-definidos", tags=["alertas definidos"])

# Criar alerta definido
@router.post("/", response_model=AlertaDefinidoResponse)
async def create_alerta_definido(
    alerta_definido: AlertaDefinidoCreate, 
    db: AsyncSession = Depends(get_async_db),
    current_user: UsuarioModel = Depends(get_current_user),
):
    # Verifica se a estação existe
    result = await db.execute(
        db.query(Estacao).filter(Estacao.id == alerta_definido.estacao_id)
    )
    db_estacao = result.scalar_one_or_none()
    if not db_estacao:
        raise HTTPException(status_code=404, detail="Estação não encontrada")
    # Verifica se o sensor existe
    result = await db.execute(
        db.query(Parametro).filter(Parametro.id == alerta_definido.parametro_id)
    )
    db_parametro = result.scalar_one_or_none()
    if not db_parametro:
        raise HTTPException(status_code=404, detail="Sensor (parâmetro) não encontrado")
    # Verifica se o sensor está vinculado à estação
    result = await db.execute(
        db.query(EstacaoParametro).filter(
            EstacaoParametro.estacao_id == alerta_definido.estacao_id,
            EstacaoParametro.parametro_id == alerta_definido.parametro_id
        )
    )
    db_link = result.scalar_one_or_none()
    if not db_link:
        raise HTTPException(status_code=400, detail="Sensor não vinculado à estação informada")

    db_alerta_definido = AlertaDefinido(**alerta_definido.dict())
    db.add(db_alerta_definido)
    await db.commit()
    await db.refresh(db_alerta_definido)
    return db_alerta_definido

# Listar todos os alertas definidos
@router.get("/", response_model=list[AlertaDefinidoResponse])
async def list_alertas_definidos(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(db.query(AlertaDefinido))
    return result.scalars().all()

# Listar alerta definido específico por ID
@router.get("/{alerta_definido_id}", response_model=AlertaDefinidoResponse)
async def get_alerta_definido(alerta_definido_id: int, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(
        db.query(AlertaDefinido).filter(AlertaDefinido.id == alerta_definido_id)
    )
    db_alerta_definido = result.scalar_one_or_none()
    if not db_alerta_definido:
        raise HTTPException(status_code=404, detail="Alerta definido não encontrado")
    return db_alerta_definido

# Atualizar alerta definido específico por ID
@router.put("/{alerta_definido_id}", response_model=AlertaDefinidoResponse)
async def update_alerta_definido(
    alerta_definido_id: int, 
    alerta_definido: AlertaDefinidoUpdate, 
    db: AsyncSession = Depends(get_async_db),
    current_user: UsuarioModel = Depends(get_current_user),
):
    result = await db.execute(
        db.query(AlertaDefinido).filter(AlertaDefinido.id == alerta_definido_id)
    )
    db_alerta_definido = result.scalar_one_or_none()
    if not db_alerta_definido:
        raise HTTPException(status_code=404, detail="Alerta definido não encontrado")
    
    # Se estiver atualizando estacao_id ou parametro_id, verificar a existência e o vínculo
    estacao_id = alerta_definido.estacao_id if alerta_definido.estacao_id is not None else db_alerta_definido.estacao_id
    parametro_id = alerta_definido.parametro_id if alerta_definido.parametro_id is not None else db_alerta_definido.parametro_id

    result = await db.execute(
        db.query(Estacao).filter(Estacao.id == estacao_id)
    )
    db_estacao = result.scalar_one_or_none()
    if not db_estacao:
        raise HTTPException(status_code=404, detail="Estação não encontrada")

    result = await db.execute(
        db.query(Parametro).filter(Parametro.id == parametro_id)
    )
    db_parametro = result.scalar_one_or_none()
    if not db_parametro:
        raise HTTPException(status_code=404, detail="Sensor (parâmetro) não encontrado")

    result = await db.execute(
        db.query(EstacaoParametro).filter(
            EstacaoParametro.estacao_id == estacao_id,
            EstacaoParametro.parametro_id == parametro_id
        )
    )
    db_link = result.scalar_one_or_none()
    if not db_link:
        raise HTTPException(status_code=400, detail="Sensor não vinculado à estação informada")
    
    for key, value in alerta_definido.dict(exclude_unset=True).items():
        setattr(db_alerta_definido, key, value)
    
    await db.commit()
    await db.refresh(db_alerta_definido)
    return db_alerta_definido

# Deletar alerta definido específico por ID
@router.delete("/{alerta_definido_id}")
async def delete_alerta_definido(
    alerta_definido_id: int, 
    db: AsyncSession = Depends(get_async_db),
    current_user: UsuarioModel = Depends(get_current_user),
):
    result = await db.execute(
        db.query(AlertaDefinido).filter(AlertaDefinido.id == alerta_definido_id)
    )
    db_alerta_definido = result.scalar_one_or_none()
    if not db_alerta_definido:
        raise HTTPException(status_code=404, detail="Alerta definido não encontrado")
    
    db.delete(db_alerta_definido)
    db.commit()
    return {"message": "Alerta definido deletado com sucesso"}
