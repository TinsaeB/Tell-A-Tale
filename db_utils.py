import sqlite3
from datetime import datetime
import os

def init_db():
    conn = sqlite3.connect('tell_a_tale.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prompt TEXT,
        tale_type TEXT,
        model TEXT,
        tale_text TEXT,
        audio_bytes BLOB,
        created_at TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

def save_tale_to_db(prompt, tale_type, model, tale_text, audio_bytes):
    conn = sqlite3.connect('tell_a_tale.db')
    c = conn.cursor()
    c.execute('''INSERT INTO tales (prompt, tale_type, model, tale_text, audio_bytes, created_at)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (prompt, tale_type, model, tale_text, audio_bytes, datetime.utcnow().isoformat()))
    conn.commit()
    tale_id = c.lastrowid
    conn.close()
    return tale_id

def get_all_tales():
    conn = sqlite3.connect('tell_a_tale.db')
    c = conn.cursor()
    c.execute('''SELECT id, prompt, tale_type, model, tale_text, created_at FROM tales ORDER BY datetime(created_at) DESC''')
    rows = c.fetchall()
    tales = []
    for row in rows:
        tales.append({
            'id': row[0],
            'prompt': row[1],
            'tale_type': row[2],
            'model': row[3],
            'tale_text': row[4],
            'created_at': datetime.fromisoformat(row[5])
        })
    conn.close()
    return tales

def search_tales(query=None, type_filter=None, model_filter=None):
    conn = sqlite3.connect('tell_a_tale.db')
    c = conn.cursor()
    sql = '''SELECT id, prompt, tale_type, model, tale_text, created_at FROM tales WHERE 1=1'''
    params = []
    if query:
        sql += " AND (prompt LIKE ? OR tale_text LIKE ?)"
        params.extend([f'%{query}%', f'%{query}%'])
    if type_filter:
        sql += " AND tale_type = ?"
        params.append(type_filter)
    if model_filter:
        sql += " AND model = ?"
        params.append(model_filter)
    sql += " ORDER BY datetime(created_at) DESC"
    c.execute(sql, params)
    rows = c.fetchall()
    tales = []
    for row in rows:
        tales.append({
            'id': row[0],
            'prompt': row[1],
            'tale_type': row[2],
            'model': row[3],
            'tale_text': row[4],
            'created_at': datetime.fromisoformat(row[5])
        })
    conn.close()
    return tales

def update_tale_text(tale_id, new_text):
    conn = sqlite3.connect('tell_a_tale.db')
    c = conn.cursor()
    c.execute('UPDATE tales SET tale_text = ? WHERE id = ?', (new_text, tale_id))
    conn.commit()
    modified = c.rowcount
    conn.close()
    return modified

def delete_tale(tale_id):
    conn = sqlite3.connect('tell_a_tale.db')
    c = conn.cursor()
    c.execute('DELETE FROM tales WHERE id = ?', (tale_id,))
    conn.commit()
    deleted = c.rowcount
    conn.close()
    return deleted

# For retrieving a specific tale with audio

def get_tale_by_id(tale_id):
    conn = sqlite3.connect('tell_a_tale.db')
    c = conn.cursor()
    c.execute('SELECT id, prompt, tale_type, model, tale_text, audio_bytes, created_at FROM tales WHERE id = ?', (tale_id,))
    row = c.fetchone()
    tale = None
    if row:
        tale = {
            'id': row[0],
            'prompt': row[1],
            'tale_type': row[2],
            'model': row[3],
            'tale_text': row[4],
            'audio_bytes': row[5],
            'created_at': datetime.fromisoformat(row[6])
        }
    conn.close()
    return tale
