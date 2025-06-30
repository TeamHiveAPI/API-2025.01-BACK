from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
    verify_hashed_refresh_token
)
from core.config import settings
from schemas.token import Token, RefreshTokenRequest
from models import Usuario as UsuarioModel, RefreshToken as RefreshTokenModel
from jose import jwt, JWTError
from sqlalchemy import delete

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(UsuarioModel).where(UsuarioModel.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.senha):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_nivel": user.nivel_acesso,
            "user_id": user.id,
            "user_nome": user.nome
        },
        expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    raw_refresh_token = create_refresh_token(
        data={
            "sub": user.email,
            "user_id": user.id,
        },
        expires_delta=refresh_token_expires
    )
    hashed_refresh_token = hash_refresh_token(raw_refresh_token)

    await db.execute(
        delete(RefreshTokenModel).where(RefreshTokenModel.user_id == user.id)
    )
    
    new_refresh_token_db = RefreshTokenModel(
        user_id=user.id,
        token=hashed_refresh_token,
        expires_at=datetime.now(timezone.utc) + refresh_token_expires,
        revoked=False
    )
    db.add(new_refresh_token_db)
    await db.commit()
    await db.refresh(new_refresh_token_db)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_nivel": user.nivel_acesso,
        "user_email": user.email,
        "user_id": user.id,
        "user_nome": user.nome,
        "refresh_token": raw_refresh_token
    }

@router.post("/refresh_token", response_model=Token)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token de atualização inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(request.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("user_id")
        
        if user_id is None:
            raise credentials_exception

        result_refresh_token_db = await db.execute(
            select(RefreshTokenModel).where(
                RefreshTokenModel.user_id == user_id,
                RefreshTokenModel.revoked == False
            )
        )
        refresh_token_db = result_refresh_token_db.scalar_one_or_none()

        if not refresh_token_db:
            raise credentials_exception

        if not verify_hashed_refresh_token(request.refresh_token, refresh_token_db.token):
            refresh_token_db.revoked = True
            await db.commit()
            raise credentials_exception

        if refresh_token_db.expires_at < datetime.now(timezone.utc):
            refresh_token_db.revoked = True
            await db.commit()
            raise credentials_exception

        result_user = await db.execute(select(UsuarioModel).where(UsuarioModel.id == user_id))
        user = result_user.scalar_one_or_none()
        if not user:
            raise credentials_exception

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = create_access_token(
            data={
                "sub": user.email,
                "user_nivel": user.nivel_acesso,
                "user_id": user.id,
                "user_nome": user.nome
            },
            expires_delta=access_token_expires
        )

        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "user_nivel": user.nivel_acesso,
            "user_email": user.email,
            "user_id": user.id,
            "user_nome": user.nome,
            "refresh_token": request.refresh_token
        }

    except JWTError:
        raise credentials_exception
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno ao processar refresh token: {str(e)}")