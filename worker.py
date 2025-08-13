# worker.py
import os
import redis
from rq import Worker, Queue

# Lista de filas que este worker irá observar. 'default' é o padrão.
listen = ['default']

# Obtém a URL de conexão do Redis a partir das variáveis de ambiente.
# Se não for encontrada, usa um valor padrão para desenvolvimento local.
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')

# Cria a conexão com o Redis a partir da URL.
conn = redis.from_url(redis_url)

if __name__ == '__main__':
    # Cria uma instância do Worker, passando a conexão e as filas.
    # O 'with Connection(conn):' não é mais necessário nesta versão da biblioteca.
    print("Iniciando Worker do Redis...")
    worker = Worker(map(Queue, listen), connection=conn)
    worker.work()

