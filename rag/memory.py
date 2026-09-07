from pathlib import Path
import sqlite3

DEFAULT_DB = Path('data') / 'conversation_memory.sqlite3'

class ConversationMemory:
    """Persistent local conversation history. Authentication is intentionally excluded."""
    def __init__(self, db_path=DEFAULT_DB):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )''')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id, id)')

    def add(self, conversation_id, role, content):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('INSERT INTO messages(conversation_id, role, content) VALUES (?,?,?)', (conversation_id, role, content))

    def history(self, conversation_id, limit=20):
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute('SELECT role, content, created_at FROM messages WHERE conversation_id=? ORDER BY id DESC LIMIT ?', (conversation_id, limit)).fetchall()
        rows.reverse()
        return [{'role': r[0], 'content': r[1], 'created_at': r[2]} for r in rows]

    def clear(self, conversation_id):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM messages WHERE conversation_id=?', (conversation_id,))
