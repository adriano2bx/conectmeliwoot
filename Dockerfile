# Dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Torna o entrypoint executável
RUN chmod +x /app/entrypoint.sh

# A porta do instalador é 8080, a do Gunicorn (webhook) é 5000
EXPOSE 5000 8080

# O entrypoint decidirá qual comando executar
ENTRYPOINT ["/app/entrypoint.sh"]
