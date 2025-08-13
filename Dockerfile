# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala as dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código da aplicação para /app
COPY . .

# --- CORREÇÃO DEFINITIVA ---
# Copia explicitamente o ficheiro de configuração do supervisor para o seu destino final.
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Torna o entrypoint executável
RUN chmod +x /app/entrypoint.sh

# Expõe as portas necessárias
EXPOSE 5000 8080

# Define o ponto de entrada
ENTRYPOINT ["/app/entrypoint.sh"]
