from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models import Usuario as UsuarioModel
from core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=10)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    start_time = datetime.now()
    hashed_password = pwd_context.hash(password)
    end_time = datetime.now()
    time_taken = (end_time - start_time).total_seconds() * 1000
    print(f"DEBUG - get_password_hash: Hashing da senha levou {time_taken:.2f} ms")
    return hashed_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        # Troque datetime.now(timezone.utc) por datetime.utcnow()
        expire = datetime.utcnow() + expires_delta
    else:
        # Troque datetime.now(timezone.utc) por datetime.utcnow()
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        # Troque datetime.now(timezone.utc) por datetime.utcnow()
        expire = datetime.utcnow() + expires_delta
    else:
        # Troque datetime.now(timezone.utc) por datetime.utcnow()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def hash_refresh_token(refresh_token: str) -> str:
    return pwd_context.hash(refresh_token)

def verify_hashed_refresh_token(plain_token: str, hashed_token: str) -> bool:
    return pwd_context.verify(plain_token, hashed_token)

# --- Validação de Token de Acesso ---
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        
        result = await db.execute(select(UsuarioModel).where(UsuarioModel.email == email))
        user = result.scalar_one_or_none()
        
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception

def check_user_level(required_level: str):
    def check(current_user: UsuarioModel = Depends(get_current_user)):
        if current_user.nivel_acesso != required_level and current_user.nivel_acesso != "ADMINISTRADOR":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para realizar esta ação."
            )
        return current_user
    return check