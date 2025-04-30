# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from database import get_db
# from models import Alerta, AlertaDefinido, Estacao
# from schemas.alerta import AlertaCreate, AlertaUpdate
# from schemas.tempo_alerta import TempoAlertaResponse
# from typing import List
# from sqlalchemy import func

# from datetime import datetime

# router = APIRouter(prefix="/tempo-em-alerta-por-estacao", tags=["tempo em alerta por estação"])

# @router.get("/", response_model=List[TempoAlertaResponse])
# def list_tempos_alerta(db: Session = Depends(get_db)):
#     # Adiciona logs para debug
#     alertas = db.query(Alerta).all()
#     print(f"Total de alertas: {len(alertas)}")
    
#     alertas_definidos = db.query(AlertaDefinido).all()
#     print(f"Total de alertas definidos: {len(alertas_definidos)}")
    
#     estacoes = db.query(Estacao).all()
#     print(f"Total de estações: {len(estacoes)}")

#     # Query original
#     resultados = db.query(
#         Estacao.nome.label('estacao'),
#         func.sum(
#             func.coalesce(
#                 func.extract('epoch', Alerta.tempoFim) - func.extract('epoch', Alerta.data_hora), 0
#             ) / 3600
#         ).label('horas_alerta_total'),
#         func.count(Alerta.id).label('qtd_alertas')
#     ).join(
#         AlertaDefinido, AlertaDefinido.id == Alerta.alerta_definido_id
#     ).join(
#         Estacao, Estacao.id == AlertaDefinido.estacao_id
#     ).group_by(Estacao.id, Estacao.nome).all()  # Adicionado Estacao.nome no group_by

#     print(f"Resultados da query: {resultados}")

#     return [
#         TempoAlertaResponse(estacao=estacao, horasAlerta=horas_alerta_total, qtdAlertas=qtd_alertas)
#         for estacao, horas_alerta_total, qtd_alertas in resultados
#     ]


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Alerta, AlertaDefinido, Estacao
from schemas.alerta import AlertaCreate, AlertaUpdate
from schemas.tempo_alerta import TempoAlertaResponse
from typing import List
from sqlalchemy import func, case

from datetime import datetime

router = APIRouter(prefix="/tempo-em-alerta-por-estacao", tags=["tempo em alerta por estação"])

@router.get("/", response_model=List[TempoAlertaResponse])
def list_tempos_alerta(db: Session = Depends(get_db)):
    # Adiciona logs para debug
    alertas = db.query(Alerta).all()
    print(f"Total de alertas: {len(alertas)}")
    
    alertas_definidos = db.query(AlertaDefinido).all()
    print(f"Total de alertas definidos: {len(alertas_definidos)}")
    
    estacoes = db.query(Estacao).all()
    print(f"Total de estações: {len(estacoes)}")

    # Query modificada para calcular o tempo corretamente
    resultados = db.query(
        Estacao.nome.label('estacao'),
        func.sum(
            case(
                # Se tempoFim é null, usa o timestamp atual
                (Alerta.tempoFim == None, 
                 func.extract('epoch', func.current_timestamp()) - func.extract('epoch', Alerta.data_hora)),
                # Senão, usa tempoFim - data_hora
                else_=func.extract('epoch', Alerta.tempoFim) - func.extract('epoch', Alerta.data_hora)
            ) / 3600  # Convertendo para horas
        ).label('horas_alerta_total'),
        func.count(Alerta.id).label('qtd_alertas')
    ).join(
        AlertaDefinido, AlertaDefinido.id == Alerta.alerta_definido_id
    ).join(
        Estacao, Estacao.id == AlertaDefinido.estacao_id
    ).group_by(Estacao.id, Estacao.nome).all()

    print(f"Resultados da query: {resultados}")

    return [
        TempoAlertaResponse(estacao=estacao, horasAlerta=float(horas_alerta_total) if horas_alerta_total else 0, qtdAlertas=qtd_alertas)
        for estacao, horas_alerta_total, qtd_alertas in resultados
    ]