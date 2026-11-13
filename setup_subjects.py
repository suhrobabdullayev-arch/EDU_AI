
import sqlite3
from pathlib import Path
import json

DB_PATH = Path(__file__).with_name("edu_ai.db")

SUBJECTS = [
    ("Informatika", "Kompyuter va axborot texnologiyalari"),
    ("Matematika", "Algebra va geometriya"),
    ("Ona tili", "O‘zbek tili grammatikasi"),
    ("Adabiyot", "Badiiy asarlar va adabiyot"),
    ("Ingliz tili", "Ingliz tili grammatikasi va lug‘at"),
    ("Fizika", "Fizik hodisalar va qonunlar"),
    ("Kimyo", "Kimyoviy elementlar va reaksiyalar"),
    ("Biologiya", "Tirik organizmlar va tabiat"),
    ("Tarix", "O‘zbekiston va jahon tarixi"),
    ("Geografiya", "Tabiat va geografik bilimlar"),
    ("Rus tili", "Rus tili grammatikasi"),
    ("Huquq", "Huquqiy bilimlar"),
    ("Tarbiya", "Ma’naviyat va tarbiya")
]

INFORMATICS_QUESTIONS = [
    ("Python asoslari",
     "Python dasturlash tilida ekranga matn chiqarish uchun qaysi buyruq ishlatiladi?",
     ["input()", "print()", "int()", "type()"], 1,
     "print() funksiyasi qiymat yoki matnni ekranga chiqaradi.",
     "print() va input() funksiyalari bo‘yicha 5 ta mashq bajaring."),

    ("Python asoslari",
     "x = 7 bo‘lsa, x ning turi qaysi?",
     ["str", "bool", "int", "list"], 2,
     "7 butun son, shuning uchun uning turi int.",
     "int, float va str turlariga 3 tadan misol yozing."),

    ("Python asoslari",
     "Ro‘yxat (list) qaysi belgi bilan yoziladi?",
     ["()", "{}", "[]", "<>"], 2,
     "Python ro‘yxatlari kvadrat qavslar ichida yoziladi.",
     "5 ta elementdan iborat list yarating."),

    ("Algoritmlar",
     "Algoritm nima?",
     ["Kompyuter qurilmasi",
      "Masalani yechish uchun aniq ketma-ket ko‘rsatmalar",
      "Faqat dasturlash tili", "Internet manzili"], 1,
     "Algoritm — masalani yechish amallari ketma-ketligi.",
     "Kundalik hayotdagi jarayon uchun algoritm tuzing."),

    ("Algoritmlar",
     "Shartni tekshirish uchun Python'da qaysi kalit so‘z ishlatiladi?",
     ["for", "if", "def", "return"], 1,
     "if operatori shartni tekshiradi.",
     "Son musbat yoki manfiyligini aniqlang."),

    ("Algoritmlar",
     "Takrorlash uchun qaysi operator ishlatiladi?",
     ["for", "print", "import", "class"], 0,
     "for takrorlash operatoridir.",
     "1 dan 10 gacha sonlarni chiqaruvchi sikl yozing."),

    ("Ikkilik sanoq sistemasi",
     "Ikkilik sanoq sistemasida qaysi raqamlar ishlatiladi?",
     ["0 va 1", "0 dan 7 gacha", "0 dan 9 gacha", "1 va 2"], 0,
     "Ikkilik sanoq sistemasida faqat 0 va 1 ishlatiladi.",
     "2, 3, 4, 5 sonlarini ikkilikka o‘tkazing."),

    ("Ikkilik sanoq sistemasi",
     "101₂ sonining o‘nlikdagi qiymati nechaga teng?",
     ["3", "4", "5", "6"], 2,
     "1×4 + 0×2 + 1×1 = 5.",
     "110₂, 111₂ va 1001₂ sonlarini o‘nlikka aylantiring."),

    ("Ikkilik sanoq sistemasi",
     "O‘nlikdagi 2 soni ikkilikda qanday yoziladi?",
     ["10", "11", "01", "100"], 0,
     "2 soni ikkilikda 10 bo‘ladi.",
     "6 dan 12 gacha sonlarni ikkilikka o‘tkazing.")
]


def create_tables(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            is_active INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS subject_grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            grade INTEGER NOT NULL CHECK(grade BETWEEN 5 AND 11),
            UNIQUE(subject_id, grade),
            FOREIGN KEY(subject_id) REFERENCES subjects(id)
        );

        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            grade INTEGER,
            FOREIGN KEY(subject_id) REFERENCES subjects(id)
        );

        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            options_json TEXT NOT NULL,
            correct_index INTEGER NOT NULL,
            explanation TEXT,
            practice_task TEXT,
            difficulty TEXT DEFAULT 'O‘rta',
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY(topic_id) REFERENCES topics(id)
        );
    """)

    # Eski test natijalari saqlanadi.
    columns = {
        row[1] for row in
        conn.execute("PRAGMA table_info(attempts)").fetchall()
    }

    if "subject_id" not in columns:
        conn.execute(
            "ALTER TABLE attempts ADD COLUMN subject_id INTEGER"
        )

    if "grade" not in columns:
        conn.execute(
            "ALTER TABLE attempts ADD COLUMN grade INTEGER"
        )


def add_subjects(conn):
    for name, description in SUBJECTS:
        conn.execute("""
            INSERT OR IGNORE INTO subjects (name, description)
            VALUES (?, ?)
        """, (name, description))

    subjects = conn.execute(
        "SELECT id FROM subjects"
    ).fetchall()

    for (subject_id,) in subjects:
        for grade in range(5, 12):
            conn.execute("""
                INSERT OR IGNORE INTO subject_grades
                (subject_id, grade)
                VALUES (?, ?)
            """, (subject_id, grade))


def add_informatics_questions(conn):
    subject = conn.execute(
        "SELECT id FROM subjects WHERE name = ?",
        ("Informatika",)
    ).fetchone()

    subject_id = subject[0]

    for topic_title, question, options, answer, explanation, task in INFORMATICS_QUESTIONS:

        topic = conn.execute("""
            SELECT id FROM topics
            WHERE subject_id = ? AND title = ? AND grade IS NULL
            LIMIT 1
        """, (subject_id, topic_title)).fetchone()

        if topic is None:
            cursor = conn.execute("""
                INSERT INTO topics (subject_id, title, grade)
                VALUES (?, ?, NULL)
            """, (subject_id, topic_title))
            topic_id = cursor.lastrowid
        else:
            topic_id = topic[0]

        exists = conn.execute("""
            SELECT id FROM questions
            WHERE topic_id = ? AND question = ?
        """, (topic_id, question)).fetchone()

        if exists is None:
            conn.execute("""
                INSERT INTO questions
                (topic_id, question, options_json,
                 correct_index, explanation, practice_task)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                topic_id,
                question,
                json.dumps(options, ensure_ascii=False),
                answer,
                explanation,
                task
            ))


def main():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        create_tables(conn)
        add_subjects(conn)
        add_informatics_questions(conn)

    print("EDU AI ma'lumotlar bazasi yangilandi!")
    print("13 ta fan qo‘shildi.")
    print("5–11-sinflar uchun fanlar biriktirildi.")
    print("Informatika savollari bazaga joylandi.")
    print("Eski foydalanuvchilar va natijalar saqlandi.")


if __name__ == "__main__":
    main()
