import json
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Enum, Boolean, ForeignKey, TIMESTAMP, Text
from sqlalchemy.orm import relationship
from database import Base
import enum
import uuid
from datetime import datetime

class StatusEstacao(enum.Enum):
    ativa = "ativa"
    inativa = "inativa"

class StatusAlerta(enum.Enum):
    ativo = "ativo"
    resolvido = "resolvido"

class Estacao(Base):
    __tablename__ = "estacao"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(100), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    nome = Column(String(100), index=True)
    cep = Column(String(9))
    rua = Column(String(100))
    bairro = Column(String(50))
    cidade = Column(String(50))
    numero = Column(String(10))
    latitude = Column(Float)
    longitude = Column(Float)
    data_instalacao = Column(Date)
    status = Column(Enum(StatusEstacao))

    parametros = relationship(
        "Parametro",
        secondary="estacao_parametros",
        back_populates="estacoes"
    )
    alertas_definidos_rel = relationship("AlertaDefinido", back_populates="estacao_rel")


class TipoParametro(Base):
    __tablename__ = "tipo_parametros"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), index=True)
    descricao = Column(String)
    json = Column(String(20)) 
    parametros = relationship("Parametro", back_populates="tipo_parametro_rel")

class Parametro(Base):
    __tablename__ = "parametros"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), index=True)
    unidade = Column(String(20))
    descricao = Column(String)
    quantidade_casas_decimais = Column(Integer)
    fator_conversao = Column(Float)
    offset = Column(Float)
    tipo_parametro_id = Column(Integer, ForeignKey("tipo_parametros.id"))
    
    tipo_parametro_rel = relationship("TipoParametro", back_populates="parametros")

    estacoes = relationship(
        "Estacao",
        secondary="estacao_parametros",
        back_populates="parametros"
    )
    alertas_definidos_rel = relationship("AlertaDefinido", back_populates="parametro_rel")


class EstacaoParametro(Base):
    __tablename__ = "estacao_parametros"
    id = Column(Integer, primary_key=True, index=True)
    estacao_id = Column(Integer, ForeignKey("estacao.id"))
    parametro_id = Column(Integer, ForeignKey("parametros.id"))


class AlertaDefinido(Base):
    __tablename__ = "alertas_definidos"
    id = Column(Integer, primary_key=True, index=True)
    estacao_id = Column(Integer, ForeignKey("estacao.id"))
    parametro_id = Column(Integer, ForeignKey("parametros.id"))
    condicao = Column(String(50))
    num_condicao = Column(Float)  
    mensagem = Column(String)
    ativo = Column(Boolean, default=True)

    estacao_rel = relationship("Estacao", back_populates="alertas_definidos_rel")
    parametro_rel = relationship("Parametro", back_populates="alertas_definidos_rel")

class Alerta(Base):
    __tablename__ = "alertas"
    id = Column(Integer, primary_key=True, index=True)
    alerta_definido_id = Column(Integer, ForeignKey("alertas_definidos.id"))
    data_hora = Column(DateTime)
    valor_medido = Column(Float)
    titulo = Column(Text, nullable=False)
    descricaoAlerta = Column(Text, nullable=False)
    estacao = Column(String(255))
    coordenadas = Column(String(50))
    tempoFim = Column(DateTime, nullable=True)
    expandido = Column(Boolean, default=False)

    alerta_definido_rel = relationship("AlertaDefinido")


class Medida(Base):
    __tablename__ = "medidas"
    id = Column(Integer, primary_key=True, index=True)
    estacao_id = Column(Integer, ForeignKey("estacao.id"))
    parametro_id = Column(Integer, ForeignKey("parametros.id"))
    valor = Column(Float)
    data_hora = Column(TIMESTAMP)


class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), index=True)
    email = Column(String(100), unique=True, index=True)
    senha = Column(String(100))
    nivel_acesso = Column(String(20))
    data_criacao = Column(DateTime, default=datetime.utcnow)

    refresh_tokens = relationship("RefreshToken", back_populates="usuario")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"))
    token = Column(String, unique=True, index=True) 
    expires_at = Column(DateTime)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="refresh_tokens")