FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependências e gunicorn
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install gunicorn \
    && python -m spacy download pt_core_news_sm

# Copia o código da aplicação
COPY . .

# Expõe a porta de serviço
EXPOSE 8000

# Usa Gunicorn + UvicornWorker
CMD ["gunicorn", "main:app", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "-w", "3", \
     "--keep-alive", "10", \
     "--timeout", "30", \
     "-b", "0.0.0.0:8000"]
