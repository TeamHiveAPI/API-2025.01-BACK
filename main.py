from fastapi import FastAPI
from database import create_tables
from contextlib import asynccontextmanager
import models  # Importa os modelos para registrá-los na Base

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

# Endpoint simples para testar
@app.get("/")
def read_root():
    return {"message": "API rodando e tabelas criadas no PostgreSQL!"}