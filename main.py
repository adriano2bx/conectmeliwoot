# main.py
import time
import schedule
import requests
from config import config
import chatwoot_api
import mercado_livre_api
import db_manager

def process_questions():
    if not config.is_configured: return
    print(f"[{time.ctime()}] Iniciando verificação de perguntas...")
    try:
        questions = mercado_livre_api.get_unanswered_questions()
        for q in questions:
            question_id = q['id']
            if db_manager.is_item_processed(question_id): continue
            print(f"Nova pergunta encontrada: ID {question_id}")
            user_id = q['from']['id']
            contact_info = chatwoot_api.find_or_create_contact(identifier=user_id, name=f"Cliente MELI (ID: {user_id})")
            item_response = requests.get(f"https://api.mercadolibre.com/items/{q['item_id']}", headers=mercado_livre_api.get_auth_header())
            item_response.raise_for_status()
            item_info = item_response.json()
            item_title = item_info.get('title', 'Produto não encontrado')
            message_body = f"**Produto:** {item_title}\n**Link:** {item_info.get('permalink', 'N/A')}\n\n**Pergunta:**\n_{q['text']}_"
            meli_attributes = {"meli_question_id": str(question_id)}
            chatwoot_api.create_conversation(inbox_id=config.CHATWOOT_QUESTIONS_INBOX_ID, contact_id=contact_info['id'], message_body=message_body, custom_attributes=meli_attributes)
            db_manager.mark_item_as_processed(question_id)
    except Exception as e:
        print(f"ERRO ao processar perguntas: {e}")
    print(f"[{time.ctime()}] Verificação de perguntas concluída.")

def process_messages():
    if not config.is_configured: return
    print(f"[{time.ctime()}] Iniciando verificação de mensagens...")
    try:
        orders = mercado_livre_api.get_recent_orders()
        for order in orders:
            pack_id = order.get('pack_id')
            if not pack_id: continue
            messages = mercado_livre_api.get_messages_for_order(pack_id)
            for msg in reversed(messages):
                msg_id = msg['id']
                if db_manager.is_item_processed(msg_id) or str(msg['from']['user_id']) == str(config.MELI_USER_ID): continue
                print(f"Nova mensagem encontrada no Pack ID {pack_id}")
                buyer = order.get('buyer', {})
                existing_conversation = chatwoot_api.search_conversation(pack_id)
                message_text, attachments = msg.get('text', ''), msg.get('attachments', [])
                if existing_conversation:
                    conversation_id = existing_conversation['id']
                    print(f"Conversa existente encontrada (ID: {conversation_id}). Adicionando nova mensagem.")
                    if not attachments:
                        if not message_text.strip(): continue
                        chatwoot_api.add_message_to_conversation(conversation_id, message_text)
                    else:
                        attachment = attachments[0]
                        file_url = attachment.get('url')
                        if not file_url: continue
                        filename = attachment.get('filename', 'anexo.jpg')
                        file_response = requests.get(file_url, timeout=30)
                        file_response.raise_for_status()
                        chatwoot_api.add_message_to_conversation(conversation_id, message_text, file_content=file_response.content, filename=filename)
                else:
                    print(f"Nenhuma conversa existente para o pack {pack_id}. Criando nova.")
                    contact_info = chatwoot_api.find_or_create_contact(identifier=buyer.get('id'), name=f"{buyer.get('first_name', '')} {buyer.get('last_name', '')}".strip(), email=buyer.get('email'))
                    meli_attributes = {"meli_pack_id": str(pack_id)}
                    if not attachments:
                        if not message_text.strip(): continue
                        message_body = f"**Início da conversa sobre a Venda #{order['id']}**\n\n_{message_text}_"
                        chatwoot_api.create_conversation(inbox_id=config.CHATWOOT_MESSAGES_INBOX_ID, contact_id=contact_info['id'], message_body=message_body, custom_attributes=meli_attributes)
                    else:
                        attachment = attachments[0]
                        file_url = attachment.get('url')
                        if not file_url: continue
                        filename = attachment.get('filename', 'anexo.jpg')
                        file_response = requests.get(file_url, timeout=30)
                        file_response.raise_for_status()
                        message_body = f"**Início da conversa sobre a Venda #{order['id']}**\n\n_{message_text}_"
                        chatwoot_api.create_conversation_with_attachment(inbox_id=config.CHATWOOT_MESSAGES_INBOX_ID, contact_id=contact_info['id'], message_body=message_body, custom_attributes=meli_attributes, file_content=file_response.content, filename=filename)
                db_manager.mark_item_as_processed(msg_id)
    except Exception as e:
        print(f"ERRO ao processar mensagens: {e}")
    print(f"[{time.ctime()}] Verificação de mensagens concluída.")

if __name__ == "__main__":
    print(f"[{time.ctime()}] >>> Iniciando serviço de Poller (V5.0) <<<")
    time.sleep(10)
    config.reload()
    if not config.is_configured:
        print("AVISO: Aplicação não configurada. O Poller ficará em espera.")
    
    schedule.every(2).minutes.do(process_questions)
    schedule.every(3).minutes.do(process_messages)
    
    while True:
        schedule.run_pending()
        time.sleep(1)
