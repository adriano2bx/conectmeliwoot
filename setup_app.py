# setup_app.py
from flask import Flask, render_template, request, redirect, url_for
import db_manager
import chatwoot_api
import mercado_livre_api
import threading
import os
import signal

AUTH_CODE = None
SHUTDOWN_EVENT = threading.Event()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save_config', methods=['POST'])
def save_config():
    for key, value in request.form.items():
        db_manager.update_setting(key.upper(), value)
    
    from config import config
    config.reload()

    try:
        webhook_url = f"{request.form['APP_URI_WEBHOOK']}/webhook"
        q_inbox = chatwoot_api.create_api_inbox("Mercado Livre - Perguntas", webhook_url)
        m_inbox = chatwoot_api.create_api_inbox("Mercado Livre - Vendas", webhook_url)
        webhook = chatwoot_api.create_webhook(webhook_url)
        
        db_manager.update_setting('CHATWOOT_QUESTIONS_INBOX_ID', str(q_inbox['id']))
        db_manager.update_setting('CHATWOOT_MESSAGES_INBOX_ID', str(m_inbox['id']))
        db_manager.update_setting('CHATWOOT_WEBHOOK_SECRET', webhook['payload']['hmac_token'])
    except Exception as e:
        return f"<h1>Erro ao configurar o Chatwoot</h1><p>{e}</p>", 500

    auth_url = f"https://auth.mercadolibre.com/authorization?response_type=code&client_id={config.MELI_APP_ID}&redirect_uri={config.REDIRECT_URI}"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    global AUTH_CODE
    code = request.args.get('code')
    if not code:
        return "<h1>Erro</h1><p>Nenhum código de autorização foi recebido.</p>", 400
    
    AUTH_CODE = code
    from config import config
    config.reload()
    tokens = mercado_livre_api.exchange_code_for_tokens(AUTH_CODE)
    db_manager.update_setting('MELI_ACCESS_TOKEN', tokens['access_token'])
    db_manager.update_setting('MELI_REFRESH_TOKEN', tokens['refresh_token'])
    
    SHUTDOWN_EVENT.set()
    return redirect(url_for('finish'))

@app.route('/finish')
def finish():
    return render_template('finish.html')

def shutdown_server():
    SHUTDOWN_EVENT.wait()
    print("Setup concluído. Desligando o servidor de instalação...")
    os.kill(os.getpid(), signal.SIGINT)

if __name__ == '__main__':
    print("--- Iniciando Servidor de Instalação na porta 8080 ---")
    db_manager.initialize_db()
    threading.Thread(target=shutdown_server, daemon=True).start()
    app.run(host='0.0.0.0', port=8080)

