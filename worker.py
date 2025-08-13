# worker.py
import os
import redis
from rq import Worker, Queue, Connection

listen = ['default']
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        print("Iniciando Worker do Redis...")
        worker = Worker(map(Queue, listen))
        worker.work()

