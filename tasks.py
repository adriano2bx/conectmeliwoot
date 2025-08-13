# tasks.py
import db_manager

def answer_question_task(question_id, content):
    import mercado_livre_api
    try:
        mercado_livre_api.answer_question(question_id, content)
        db_manager.mark_item_as_processed(f"answered-{question_id}")
        print(f"WORKER: Resposta para pergunta {question_id} enviada com sucesso.")
    except Exception as e:
        print(f"WORKER: ERRO ao responder pergunta {question_id}: {e}")
        raise

def send_post_sale_message_task(pack_id, content):
    import mercado_livre_api
    try:
        mercado_livre_api.send_post_sale_message(pack_id, content)
        print(f"WORKER: Mensagem de texto para o pack {pack_id} enviada com sucesso.")
    except Exception as e:
        print(f"WORKER: ERRO ao enviar texto para o pack {pack_id}: {e}")
        raise

def send_post_sale_attachment_task(pack_id, file_content_b64, filename):
    import base64
    import mercado_livre_api
    try:
        file_content = base64.b64decode(file_content_b64)
        mercado_livre_api.send_post_sale_attachment(pack_id, file_content, filename)
        print(f"WORKER: Anexo para o pack {pack_id} enviado com sucesso.")
    except Exception as e:
        print(f"WORKER: ERRO ao enviar anexo para o pack {pack_id}: {e}")
        raise
