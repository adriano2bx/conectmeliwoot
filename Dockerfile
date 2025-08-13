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

# Copia TODOS os arquivos do seu projeto para o diretório /app
COPY . .

# Garante que o arquivo de configuração do supervisor está no lugar certo
# Este comando agora copia o arquivo de dentro do diretório /app
# para o seu destino final.
RUN cp /app/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Torna o entrypoint executável
RUN chmod +x /app/entrypoint.sh

# Expõe as portas necessárias
EXPOSE 5000 8080

# Define o ponto de entrada que irá iniciar a aplicação
ENTRYPOINT ["/app/entrypoint.sh"]
