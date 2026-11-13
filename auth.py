
import sqlite3
import hashlib
import secrets
import hmac
import re
from pathlib import Path

DB_PATH = Path(__file__).with_name("edu_ai.db")
ITERATIONS = 310_000

ROLES = ("admin", "teacher", "student")


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_auth():
    """Foydalanuvchilar jadvalini yaratadi."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT NOT NULL,
                grade INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )
        """)
        conn.commit()


def hash_password(password, salt):
    password_bytes = password.encode("utf-8")
    salt_bytes = bytes.fromhex(salt)

    result = hashlib.pbkdf2_hmac(
        "sha256",
        password_bytes,
        salt_bytes,
        ITERATIONS
    )
    return result.hex()


def create_user(username, full_name, password,
                role="student", grade=None):

    username = username.strip().lower()
    full_name = full_name.strip()

    if not re.fullmatch(r"[a-z0-9_.-]{3,30}", username):
        raise ValueError(
            "Login 3–30 belgidan iborat bo‘lsin. "
            "Faqat lotin harflari, raqam, nuqta va tire ishlating."
        )

    if len(password) < 8:
        raise ValueError("Parol kamida 8 ta belgidan iborat bo‘lsin.")

    if not full_name:
        raise ValueError("Ism-familiya kiritilishi kerak.")

    if role not in ROLES:
        raise ValueError("Foydalanuvchi roli noto‘g‘ri.")

    if role == "student":
        if grade not in range(5, 12):
            raise ValueError("O‘quvchi sinfi 5 dan 11 gacha bo‘lishi kerak.")

    salt = secrets.token_hex(16)
    password_hash = hash_password(password, salt)

    try:
        with get_connection() as conn:
            conn.execute("""
                INSERT INTO users
                (username, full_name, password_hash, salt, role, grade)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                username, full_name, password_hash,
                salt, role, grade
            ))
            conn.commit()
        return True

    except sqlite3.IntegrityError:
        raise ValueError("Bu login avval ro‘yxatdan o‘tgan.")


def authenticate(username, password):
    """Login va parolni tekshiradi."""
    username = username.strip().lower()

    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        user = conn.execute("""
            SELECT * FROM users
            WHERE username = ? AND is_active = 1
        """, (username,)).fetchone()

    if user is None:
        return None

    entered_hash = hash_password(password, user["salt"])

    if not hmac.compare_digest(
        entered_hash,
        user["password_hash"]
    ):
        return None

    return {
        "id": user["id"],
        "username": user["username"],
        "full_name": user["full_name"],
        "role": user["role"],
        "grade": user["grade"]
    }


def get_all_users():
    """Administrator uchun foydalanuvchilar ro‘yxati."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        users = conn.execute("""
            SELECT id, username, full_name, role,
                   grade, created_at, is_active
            FROM users
            ORDER BY id DESC
        """).fetchall()

    return [dict(user) for user in users]
