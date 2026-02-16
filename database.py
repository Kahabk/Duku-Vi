import sqlite3
import numpy as np
from datetime import datetime

DB_PATH = 'luna_data.db'

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
couser = conn.cursor()


def init_db():
    couser.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            face_embedding BLOB NOT NULL,
            age INTEGER,
            gender TEXT,
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen DATETIME
        )
    """)

    couser.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            speaker TEXT NOT NULL,
            massage TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()


def add_user(name, face_embedding, age=None, gender=None, note=None):

    # Use float64 for consistency with face_recognition
    emmbedding_bytes = np.array(face_embedding, dtype=np.float64).tobytes()

    couser.execute(
        "INSERT INTO users (name, face_embedding, last_seen) VALUES (?, ?, ?)",
        (name, emmbedding_bytes, datetime.now())
    )

    conn.commit()
    return couser.lastrowid


def find_user_by_embedding(face_embedding, threshold=0.5):

    couser.execute("SELECT id, name, face_embedding FROM users")
    rows = couser.fetchall()

    if not rows:
        return None

    known_encodings = []
    user_ids = []
    names = []

    for row in rows:
        user_id, name, embedding_blob = row
        try:
            emb = np.frombuffer(embedding_blob, dtype=np.float64).reshape((128,))
        except:
            continue

        known_encodings.append(emb)
        user_ids.append(user_id)
        names.append(name)

    if not known_encodings:
        return None

    import face_recognition
    distances = face_recognition.face_distance(known_encodings, face_embedding)
    best_index = np.argmin(distances)

    if distances[best_index] < threshold:
        return {
            'id': user_ids[best_index],
            'name': names[best_index]
        }

    return None


def insert_conversation(user_id, speaker, message):

    couser.execute(
        "INSERT INTO conversations (user_id, speaker, massage) VALUES (?, ?, ?)",
        (user_id, speaker, message)
    )

    conn.commit()


def enforce_memmory_limit(user_id, limit=10):

    couser.execute("""
        DELETE FROM conversations
        WHERE user_id = ?
        AND id NOT IN (
            SELECT id FROM conversations
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
        )
    """, (user_id, user_id, limit))

    conn.commit()


def load_last_conversations(user_id, limit=10):

    couser.execute("""
        SELECT speaker, massage FROM conversations
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT ?
    """, (user_id, limit))

    rows = couser.fetchall()

    return rows[::-1]


def update_user_last_seen(user_id):

    couser.execute(
        "UPDATE users SET last_seen = ? WHERE id = ?",
        (datetime.now(), user_id)
    )

    conn.commit()