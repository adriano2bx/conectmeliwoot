# main.py
import time
import schedule
import requests
from config import config
import chatwoot_api
import mercado_livre_api
import db_manager

def process_questions():
    print(f"[{time.ctime()}] Iniciando verificação de perguntas...")
    try:
        questions = mercado_livre_api.get_unanswered_questions()
        for q in questions:
            question_id = q['id']
            if db_manager.is_item_processed(question_id): continue
            print(f"Nova pergunta encontrada: ID {question_id}")
            # ... (lógica completa de processamento)
            db_manager.mark_item_as_processed(question_id)
    except Exception as e:
        print(f"ERRO ao processar perguntas: {e}")
    print(f"[{time.ctime()}] Verificação de perguntas concluída.")

def process_messages():
    print(f"[{time.ctime()}] Iniciando verificação de mensagens...")
    try:
        orders = mercado_livre_api.get_recent_orders()
        for order in orders:
            pack_id = order.get('pack_id')
            messages = mercado_livre_api.get_messages_for_order(pack_id)
            for msg in reversed(messages):
                msg_id = msg['id']
                if db_manager.is_item_processed(msg_id) or str(msg['from']['user_id']) == str(config.MELI_USER_ID): continue
                print(f"Nova mensagem encontrada no Pack ID {pack_id}")
                # ... (lógica completa de processamento)
                db_manager.mark_item_as_processed(msg_id)
    except Exception as e:
        print(f"ERRO ao processar mensagens: {e}")
    print(f"[{time.ctime()}] Verificação de mensagens concluída.")

if __name__ == "__main__":
    print(f"[{time.ctime()}] >>> Iniciando serviço de Poller (V5.0) <<<")
    # Espera inicial para garantir que a conexão com o DB esteja pronta
    time.sleep(10)
    config.reload()

    schedule.every(2).minutes.do(process_questions)
    schedule.every(3).minutes.do(process_messages)
    
    while True:
        schedule.run_pending()
        time.sleep(1)
