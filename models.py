from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Enum, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from database import Base
import enum

# Enums
class StatusEstacao(enum.Enum):
    ativa = "ativa"
    inativa = "inativa"

class StatusAlerta(enum.Enum):
    ativo = "ativo"
    resolvido = "resolvido"

# Tabela: estacao
class Estacao(Base):
    __tablename__ = "estacao"
    id = Column(Integer, primary_key=True, index=True)
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

# Tabela: tipo_parametros
class TipoParametro(Base):
    __tablename__ = "tipo_parametros"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), index=True)
    descricao = Column(String)

# Tabela: parametros
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

# Tabela: alertas_definidos
class AlertaDefinido(Base):
    __tablename__ = "alertas_definidos"
    id = Column(Integer, primary_key=True, index=True)
    estacao_id = Column(Integer, ForeignKey("estacao.id"))
    parametro_id = Column(Integer, ForeignKey("parametros.id"))
    condicao = Column(String(50))
    mensagem = Column(String)
    ativo = Column(Boolean, default=True)

# Tabela: alertas
class Alerta(Base):
    __tablename__ = "alertas"
    id = Column(Integer, primary_key=True, index=True)
    alerta_definido_id = Column(Integer, ForeignKey("alertas_definidos.id"))
    data_hora = Column(DateTime)
    valor_medido = Column(Float)

# Tabela: medidas
class Medida(Base):
    __tablename__ = "medidas"
    id = Column(Integer, primary_key=True, index=True)
    estacao_id = Column(Integer, ForeignKey("estacao.id"))
    parametro_id = Column(Integer, ForeignKey("parametros.id"))
    valor = Column(Float)
    data_hora = Column(DateTime)

# Tabela: usuarios
class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), index=True)
    email = Column(String(100), unique=True, index=True)
    senha = Column(String(100))
    nivel_acesso = Column(String(20))
    data_criacao = Column(DateTime)