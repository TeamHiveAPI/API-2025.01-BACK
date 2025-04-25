from datetime import timedelta
from sqlalchemy.orm import Session
from database import get_db
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
        self._db: Session = next(get_db())

    def execute(self) -> None:
        try:
            self._create_test_user()
            self._create_token()
            print(f"\n🔐 TOKEN FIXO PARA TESTES:\n{self._token}\n")
        except Exception as e:
            print(f"❌ Erro ao criar usuário de teste: {e}")

    def _create_test_user(self):
        self._user = self._db.query(Usuario).filter(Usuario.email == TEST_EMAIL).first()

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
            self._db.commit()
            self._db.refresh(self._user)
            print("✅ Usuário de teste criado.")

    def _create_token(self):
        self._token = create_access_token(
            data={
                "sub": self._user.email,
                "user_nivel": self._user.nivel_acesso,
                "user_id": self._user.id
            },
            expires_delta=timedelta(days=999)
        )
