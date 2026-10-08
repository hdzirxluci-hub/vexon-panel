import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
import uuid as uuid_lib

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'panel.db')


def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """ساخت جداول اولیه"""
    conn = get_db()
    c = conn.cursor()

    # جدول ادمین
    c.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')

    # جدول تنظیمات (UUID، WS_PATH، دامنه و...)
    c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

    conn.commit()
    conn.close()


# ===== عملیات ادمین =====
def is_setup_complete():
    """آیا نصب اولیه انجام شده؟"""
    conn = get_db()
    row = conn.execute('SELECT COUNT(*) as c FROM admin').fetchone()
    conn.close()
    return row['c'] > 0


def create_admin(username, password):
    conn = get_db()
    conn.execute(
        'INSERT INTO admin (username, password_hash) VALUES (?, ?)',
        (username, generate_password_hash(password))
    )
    conn.commit()
    conn.close()


def verify_admin(username, password):
    conn = get_db()
    row = conn.execute('SELECT * FROM admin WHERE username = ?', (username,)).fetchone()
    conn.close()
    if row and check_password_hash(row['password_hash'], password):
        return True
    return False


# ===== عملیات تنظیمات =====
def get_setting(key, default=None):
    conn = get_db()
    row = conn.execute('SELECT value FROM settings WHERE key = ?', (key,)).fetchone()
    conn.close()
    return row['value'] if row else default


def set_setting(key, value):
    conn = get_db()
    conn.execute(
        'INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = ?',
        (key, value, value)
    )
    conn.commit()
    conn.close()


def init_default_settings():
    """تنظیمات پیشفرض اگه نبود، بساز"""
    if not get_setting('xray_uuid'):
        set_setting('xray_uuid', str(uuid_lib.uuid4()))
    if not get_setting('ws_path'):
        set_setting('ws_path', 'xray' + str(uuid_lib.uuid4())[:8])