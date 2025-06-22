from datetime import timedelta
from sqlalchemy.orm import Session
from database import get_async_db
from models import Usuario
from datetime import datetime
from core.security import get_password_hash, create_access_token

TEST_EMAIL = "teste@teste.com"
TEST_SENHA = "teste"
TEST_NIVEL = "ADMINISTRADOR"

class CreateTestUserAndToken:
    def __init__(self):
        self._user: Usuario | None = None
        self._token: str | None = None
        self._db = None

    async def execute(self) -> None:
        try:
            async for session in get_async_db():
                self._db = session
                await self._create_test_user()
                await self._create_token()
                print(f"\n🔐 TOKEN FIXO PARA TESTES:\n{self._token}\n")
        except Exception as e:
            print(f"❌ Erro ao criar usuário de teste: {e}")

    async def _create_test_user(self):
        from sqlalchemy import select
        result = await self._db.execute(
            select(Usuario).where(Usuario.email == TEST_EMAIL)
        )
        self._user = result.scalar_one_or_none()

        if self._user:
            print("✅ Usuário de teste já existe.")
        else:
            hashed_password = get_password_hash(TEST_SENHA)
            self._user = Usuario(
                nome="Usuário de Teste",
                email=TEST_EMAIL,
                senha=hashed_password,
                nivel_acesso=TEST_NIVEL,
                data_criacao=datetime.now()
            )
            self._db.add(self._user)
            await self._db.commit()
            await self._db.refresh(self._user)
            print("✅ Usuário de teste criado.")

    async def _create_token(self):
        self._token = create_access_token(
            data={
                "sub": self._user.email,
                "user_nivel": self._user.nivel_acesso,
                "user_id": self._user.id
            },
            expires_delta=timedelta(days=999)
        )
