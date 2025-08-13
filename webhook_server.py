# webhook_server.py
import json
import base64
import requests
from flask import Flask, request
from redis import Redis
from rq import Queue
import db_manager
from config import config

app = Flask(__name__)
q = Queue(connection=Redis.from_url(config.REDIS_URL))

@app.route('/webhook', methods=['POST'])
def chatwoot_webhook():
    payload = request.json
    if payload.get('event') == 'message_created' and payload.get('message_type') == 'outgoing':
        print("WEB: Recebida resposta de um agente. Enfileirando tarefa...")
        content = payload.get('content')
        attachments = payload.get('attachments', [])
        custom_attributes = payload.get('conversation', {}).get('custom_attributes', {})
        
        if 'meli_question_id' in custom_attributes and content and content.strip():
            question_id = custom_attributes['meli_question_id']
            if not db_manager.is_item_processed(f"answered-{question_id}"):
                q.enqueue('tasks.answer_question_task', question_id, content)
                print(f"WEB: Tarefa de resposta para a pergunta {question_id} enfileirada.")
        elif 'meli_pack_id' in custom_attributes:
            pack_id = custom_attributes['meli_pack_id']
            # ... (lógica completa de enfileiramento)
    return {'status': 'enqueued'}, 200

if __name__ == '__main__':
    app.run(port=5000, debug=False)
