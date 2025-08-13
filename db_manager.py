# db_manager.py
import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    if not DATABASE_URL:
        raise ValueError("A variável de ambiente DATABASE_URL não está definida.")
    return psycopg2.connect(DATABASE_URL)

def initialize_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS meli_cw_settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)')
    cursor.execute('CREATE TABLE IF NOT EXISTS meli_cw_processed_items (item_id TEXT PRIMARY KEY)')
    conn.commit()
    cursor.close()
    conn.close()

def get_setting(key):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM meli_cw_settings WHERE key = %s", (key,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else None

def update_setting(key, value):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO meli_cw_settings (key, value) VALUES (%s, %s) ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value', (key, value))
    conn.commit()
    cursor.close()
    conn.close()

def is_item_processed(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT item_id FROM meli_cw_processed_items WHERE item_id = %s", (str(item_id),))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row is not None

def mark_item_as_processed(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO meli_cw_processed_items (item_id) VALUES (%s) ON CONFLICT (item_id) DO NOTHING", (str(item_id),))
    conn.commit()
    cursor.close()
    conn.close()

