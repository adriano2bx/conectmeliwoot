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
    # Cria uma lista de objetos Queue, passando a conexão para cada um.
    queues = [Queue(name, connection=conn) for name in listen]
    
    # Cria uma instância do Worker, passando a lista de Queues e a conexão.
    print("Iniciando Worker do Redis...")
    worker = Worker(queues, connection=conn)
    worker.work()
