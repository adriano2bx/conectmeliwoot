# config.py
import os
import db_manager

class AppConfig:
    def __init__(self):
        self.reload()

    def reload(self):
        try:
            db_manager.initialize_db()
            self.MELI_APP_ID = db_manager.get_setting("MELI_APP_ID")
            self.MELI_SECRET_KEY = db_manager.get_setting("MELI_SECRET_KEY")
            self.MELI_USER_ID = db_manager.get_setting("MELI_USER_ID")
            self.REDIRECT_URI = db_manager.get_setting("REDIRECT_URI")
            self.MELI_ACCESS_TOKEN = db_manager.get_setting("MELI_ACCESS_TOKEN")
            self.MELI_REFRESH_TOKEN = db_manager.get_setting("MELI_REFRESH_TOKEN")
            self.CHATWOOT_URL = db_manager.get_setting("CHATWOOT_URL")
            self.CHATWOOT_API_TOKEN = db_manager.get_setting("CHATWOOT_API_TOKEN")
            self.CHATWOOT_ACCOUNT_ID = db_manager.get_setting("CHATWOOT_ACCOUNT_ID")
            self.CHATWOOT_QUESTIONS_INBOX_ID = db_manager.get_setting("CHATWOOT_QUESTIONS_INBOX_ID")
            self.CHATWOOT_MESSAGES_INBOX_ID = db_manager.get_setting("CHATWOOT_MESSAGES_INBOX_ID")
            self.CHATWOOT_WEBHOOK_SECRET = db_manager.get_setting("CHATWOOT_WEBHOOK_SECRET")
            self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
        except Exception as e:
            print(f"AVISO: Não foi possível carregar as configurações do banco de dados: {e}")
            print("Isso é normal durante o processo de setup inicial.")

config = AppConfig()

def update_meli_tokens(new_access_token, new_refresh_token):
    db_manager.update_setting('MELI_ACCESS_TOKEN', new_access_token)
    db_manager.update_setting('MELI_REFRESH_TOKEN', new_refresh_token)
    config.reload()
