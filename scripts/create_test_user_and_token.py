import os
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from core.security import get_password_hash, create_access_token
from core.config import settings
from models import Usuario as UsuarioModel
from database import get_db

class CreateTestUserAndToken:
    def __init__(self):
        pass 

    async def execute(self):
        async for db in get_db(): 
            try:
                result = await db.execute(select(UsuarioModel).where(UsuarioModel.email == "teste@email.com"))
                existing_user = result.scalar_one_or_none()

                if existing_user:
                    print("Usuário de teste já existe. Pulando criação.")
                    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
                    access_token = create_access_token(
                        data={
                            "sub": existing_user.email,
                            "user_nivel": existing_user.nivel_acesso,
                            "user_id": existing_user.id,
                        },
                        expires_delta=access_token_expires
                    )
                    print(f"Token de acesso para usuário de teste (existente): {access_token}")
                    return
                
                senha_hash = get_password_hash("teste123")
                test_user = UsuarioModel(
                    nome="Usuario Teste",
                    email="teste@email.com",
                    senha=senha_hash,
                    nivel_acesso="ADMINISTRADOR",
                    data_criacao=datetime.now()
                )
                db.add(test_user)
                await db.commit()
                await db.refresh(test_user)

                access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
                access_token = create_access_token(
                    data={
                        "sub": test_user.email,
                        "user_nivel": test_user.nivel_acesso,
                        "user_id": test_user.id,
                    },
                    expires_delta=access_token_expires
                )

                print("Usuário de teste 'teste@email.com' criado com sucesso.")
                print(f"Token de acesso para usuário de teste: {access_token}")

            except Exception as e:
                await db.rollback()
                print(f"Erro ao criar usuário de teste e token: {e}")
                raise