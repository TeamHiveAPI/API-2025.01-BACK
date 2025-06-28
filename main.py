from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import create_tables_async

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

from scripts.create_test_user_and_token import CreateTestUserAndToken

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables_async()
    
    await CreateTestUserAndToken().execute()
    yield

app = FastAPI(
    title="Weather Station API",
    description="API para gerenciamento de estações meteorológicas",
    version="0.1.0",
    lifespan=lifespan
)

# Configuração do CORS
origins = [
    "http://localhost:5173",
    "http://localhost:8001"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

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
async def read_root():
    return {"message": "API rodando e tabelas criadas no PostgreSQL!"}