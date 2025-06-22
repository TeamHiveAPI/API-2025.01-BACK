from fastapi import FastAPI # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from contextlib import asynccontextmanager
import models
from database import create_tables
from scripts.create_test_user_and_token import CreateTestUserAndToken
from routes import (
    estacoes,
    pesquisa, 
    usuario, 
    alerta, 
    alerta_definido, 
    parametro,
    tipo_parametro, 
    auth,
    medida,
    dashboard,
    tempo_alerta
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    await CreateTestUserAndToken().execute()
    yield

app = FastAPI(
    title="Weather Station API",
    description="API para gerenciamento de estações meteorológicas",
    version="0.1.0",
    lifespan=lifespan
)

# Configuração do CORS
origins = ["*"]  # Permite todas as origens durante desenvolvimento

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,         # Permite requisições do domínio listado
    allow_credentials=True,        # Permite envio de cookies, se necessário
    allow_methods=["*"],           # Permite todos os métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],           # Permite todos os cabeçalhos
)

# Inclusão das rotas

app.include_router(estacoes.router)
app.include_router(parametro.router)
app.include_router(tipo_parametro.router)
app.include_router(auth.router)
app.include_router(usuario.router)
app.include_router(alerta.router)
app.include_router(alerta_definido.router)
app.include_router(dashboard.router)
app.include_router(medida.router)
app.include_router(tempo_alerta.router)
app.include_router(pesquisa.router)

@app.get("/")
def read_root():
    return {"message": "API rodando e tabelas criadas no PostgreSQL!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}