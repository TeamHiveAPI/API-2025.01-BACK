from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import create_tables
from contextlib import asynccontextmanager
import models
from routes import parametro, tipo_parametro

# Definindo o manipulador de ciclo de vida
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()  # Executa ao iniciar a aplicação
    yield  # Mantém a aplicação rodando

# Criando a aplicação com o lifespan
app = FastAPI(
    title="Weather Station API",
    description="API para gerenciamento de estações meteorológicas",
    version="0.1.0",
    lifespan=lifespan
)

# Configuração do CORS
origins = [
    "http://localhost:5173",  # Frontend do React
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,         # Permite requisições do domínio listado
    allow_credentials=True,        # Permite envio de cookies, se necessário
    allow_methods=["*"],           # Permite todos os métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],           # Permite todos os cabeçalhos
)

app.include_router(parametro.router)
app.include_router(tipo_parametro.router)

# Endpoint simples para testar
@app.get("/")
def read_root():
    return {"message": "API rodando e tabelas criadas no PostgreSQL!"}