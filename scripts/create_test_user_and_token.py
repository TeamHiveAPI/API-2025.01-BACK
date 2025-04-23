from datetime import timedelta
from sqlalchemy.orm import Session
from database import get_db
from models import Usuario
from datetime import datetime
from core.security import get_password_hash, create_access_token

TEST_EMAIL = "teste@teste.com"
TEST_SENHA = "teste"
TEST_NIVEL = "ADMINISTRADOR"

def create_test_user_and_token():
    db_gen = get_db()
    db: Session = next(db_gen)

    user = db.query(Usuario).filter(Usuario.email == TEST_EMAIL).first()

    if user:
        print("✅ Usuário de teste já existe.")
    else:
        hashed_password = get_password_hash(TEST_SENHA)
        user = Usuario(
            nome="Usuário de Teste",
            email=TEST_EMAIL,
            senha=hashed_password,
            nivel_acesso=TEST_NIVEL,
            data_criacao=datetime.now()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print("✅ Usuário de teste criado.")

    token = create_access_token(
        data={
            "sub": user.email,
            "user_email": user.email,
            "user_nivel": user.nivel_acesso,
            "user_id": user.id
        },
        expires_delta=timedelta(days=999)
    )

    print(f"\n🔐 TOKEN FIXO PARA TESTES:\n{token}\n")
