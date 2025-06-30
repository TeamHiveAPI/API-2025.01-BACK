FROM python:3.11-slim-buster as builder

WORKDIR /app

RUN apt-get update && \
    apt-get install -y build-essential wget && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN python -m spacy download pt_core_news_sm

FROM python:3.11-slim-buster

WORKDIR /app

RUN adduser --system --no-create-home --group appuser

RUN chown -R appuser:appuser /app

USER appuser

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/ /usr/local/bin/

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--log-level", "info"]
