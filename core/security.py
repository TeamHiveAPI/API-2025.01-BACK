from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from models import Usuario as UsuarioModel
from database import get_async_db
from core.config import settings
from schemas.usuario import UsuarioResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = HTTPBearer()

class GetUserByEmailController:
    @staticmethod
    async def execute(session: AsyncSession, email: str) -> UsuarioResponse | None:
        from sqlalchemy import select
        result = await session.execute(
            select(UsuarioModel).where(UsuarioModel.email == email)
        )
        user = result.scalar_one_or_none()
        formated_user = UsuarioResponse.from_orm(user) if user else None
        return formated_user

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_user_by_email(db: AsyncSession, email: str) -> UsuarioModel | None:
    from sqlalchemy import select
    result = await db.execute(
        select(UsuarioModel).where(UsuarioModel.email == email)
    )
    return result.scalar_one_or_none()

async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token_str = token.credentials
        payload = jwt.decode(token_str, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_email(db, email)
    if user is None:
        raise credentials_exception
    return user

def verify_user_nivel(
    token: HTTPAuthorizationCredentials  = Depends(oauth2_scheme), 
    required_nivel: str | None = None
) -> bool:
    try:
        token_str = token.credentials
        payload = jwt.decode(token_str, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_nivel = payload.get("user_nivel")
        if user_nivel is None:
            return False
        return user_nivel == required_nivel
    except JWTError:
        return False

def require_user_nivel(required_nivel: str):
    async def dependency(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)) -> bool:
        if not verify_user_nivel(token, required_nivel):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User nivel {required_nivel} required"
            )
        return True
    return dependency