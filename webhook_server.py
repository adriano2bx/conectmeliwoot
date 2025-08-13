# webhook_server.py
import json
import base64
import requests
import hmac
import hashlib
from flask import Flask, request, abort
from redis import Redis
from rq import Queue
import db_manager
from config import config

app = Flask(__name__)
q = None

def get_queue():
    global q
    if q is None:
        q = Queue(connection=Redis.from_url(config.REDIS_URL))
    return q

def verify_signature(payload_body, signature_header):
    if not config.CHATWOOT_WEBHOOK_SECRET or not signature_header or not payload_body:
        return False
    secret = config.CHATWOOT_WEBHOOK_SECRET.encode('utf-8')
    signature = signature_header.replace('sha256=', '')
    digest = hmac.new(secret, msg=payload_body, digestmod=hashlib.sha256).hexdigest()
    return hmac.compare_digest(digest, signature)

@app.before_request
def before_request_func():
    # Esta função garante que a configuração seja carregada na primeira requisição
    # em um ambiente de produção com múltiplos workers (gunicorn).
    if not config.is_configured:
        config.reload()

@app.route('/webhook', methods=['POST'])
def chatwoot_webhook():
    if not config.is_configured:
        return {'status': 'unconfigured'}, 503
    
    # Reativando a verificação de segurança, pois o setup agora a configura.
    if not verify_signature(request.data, request.headers.get('X-Chatwoot-Hmac-Sha256')):
        print("ALERTA DE SEGURANÇA: Assinatura HMAC inválida.")
        abort(401)

    payload = request.json
    if payload.get('event') == 'message_created' and payload.get('message_type') == 'outgoing':
        print("WEB: Recebida resposta de um agente. Enfileirando tarefa...")
        content = payload.get('content')
        attachments = payload.get('attachments', [])
        custom_attributes = payload.get('conversation', {}).get('custom_attributes', {})
        queue = get_queue()

        if 'meli_question_id' in custom_attributes and content and content.strip():
            question_id = custom_attributes['meli_question_id']
            if not db_manager.is_item_processed(f"answered-{question_id}"):
                queue.enqueue('tasks.answer_question_task', question_id, content)
                print(f"WEB: Tarefa de resposta para a pergunta {question_id} enfileirada.")
        elif 'meli_pack_id' in custom_attributes:
            pack_id = custom_attributes['meli_pack_id']
            if content and content.strip():
                queue.enqueue('tasks.send_post_sale_message_task', pack_id, content)
            if attachments:
                for attachment in attachments:
                    try:
                        file_response = requests.get(attachment.get('data_url'), timeout=30)
                        file_response.raise_for_status()
                        file_content_b64 = base64.b64encode(file_response.content).decode('utf-8')
                        queue.enqueue('tasks.send_post_sale_attachment_task', pack_id, file_content_b64, attachment.get('filename'))
                    except Exception as e:
                        print(f"WEB: ERRO ao enfileirar tarefa de anexo: {e}")
    return {'status': 'enqueued'}, 200
