import streamlit as st
import sqlite3
from datetime import datetime
from collections import defaultdict

DB_PATH = "edu_ai.db"

QUESTIONS = [
    {"id": 1, "topic": "Python asoslari", "q": "Python dasturlash tilida ekranga matn chiqarish uchun qaysi buyruq ishlatiladi?",
     "opts": ["input()", "print()", "int()", "type()"], "a": 1,
     "why": "print() funksiyasi qiymat yoki matnni ekranga chiqaradi.",
     "task": "print() va input() funksiyalari bo‘yicha 5 ta kichik mashq bajaring."},
    {"id": 2, "topic": "Python asoslari", "q": "x = 7 bo‘lsa, x ning turi qaysi?",
     "opts": ["str", "bool", "int", "list"], "a": 2,
     "why": "7 butun son, shuning uchun uning turi int.", "task": "int, float va str turlariga 3 tadan misol yozing."},
    {"id": 3, "topic": "Python asoslari", "q": "Ro‘yxat (list) qaysi belgi bilan yoziladi?",
     "opts": ["()", "{}", "[]", "<>"], "a": 2,
     "why": "Python ro‘yxatlari kvadrat qavslar ichida yoziladi.", "task": "5 ta elementdan iborat list yarating va elementlarini chiqaring."},
    {"id": 4, "topic": "Algoritmlar", "q": "Algoritm nima?",
     "opts": ["Kompyuter qurilmasi", "Masalani yechish uchun aniq ketma-ket ko‘rsatmalar", "Faqat dasturlash tili", "Internet manzili"], "a": 1,
     "why": "Algoritm — muammoni hal qilishga olib boradigan aniq amallar ketma-ketligi.", "task": "Kundalik hayotdagi bir jarayon uchun 6–8 qadamli algoritm tuzing."},
    {"id": 5, "topic": "Algoritmlar", "q": "Shartni tekshirish uchun Python'da qaysi kalit so‘z ishlatiladi?",
     "opts": ["for", "if", "def", "return"], "a": 1,
     "why": "if operatori shartni tekshiradi.", "task": "Son musbat yoki manfiyligini if yordamida aniqlang."},
    {"id": 6, "topic": "Algoritmlar", "q": "Takrorlash (sikl) uchun qaysi operator ishlatiladi?",
     "opts": ["for", "print", "import", "class"], "a": 0,
     "why": "for operatori ketma-ketlik elementlari bo‘yicha takrorlashni tashkil qiladi.", "task": "1 dan 10 gacha sonlarni chiqaruvchi sikl yozing."},
    {"id": 7, "topic": "Ikkilik sanoq sistemasi", "q": "Ikkilik sanoq sistemasida qaysi raqamlar ishlatiladi?",
     "opts": ["0 va 1", "0 dan 7 gacha", "0 dan 9 gacha", "1 va 2"], "a": 0,
     "why": "Ikkilik sanoq sistemasining asosi 2 bo‘lib, faqat 0 va 1 ishlatiladi.", "task": "2, 3, 4, 5 sonlarini ikkilik sanoq sistemasiga o‘tkazing."},
    {"id": 8, "topic": "Ikkilik sanoq sistemasi", "q": "101₂ sonining o‘nlik sanoq sistemasidagi qiymati nechaga teng?",
     "opts": ["3", "4", "5", "6"], "a": 2,
     "why": "1×4 + 0×2 + 1×1 = 5.", "task": "110₂, 111₂ va 1001₂ sonlarini o‘nlikka aylantiring."},
    {"id": 9, "topic": "Ikkilik sanoq sistemasi", "q": "O‘nlik sanoq sistemasidagi 2 soni ikkilikda qanday yoziladi?",
     "opts": ["10", "11", "01", "100"], "a": 0,
     "why": "2 = 1×2 + 0, demak 10₂.", "task": "6 dan 12 gacha sonlarni ikkilik sanoq sistemasiga o‘tkazing."},
]

def init_db():
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student TEXT NOT NULL,
            created_at TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            topic_scores TEXT NOT NULL
        )""")

def save_attempt(student, score, total, topic_scores):
    with sqlite3.connect(DB_PATH) as con:
        con.execute(
            "INSERT INTO attempts(student, created_at, score, total, topic_scores) VALUES (?, ?, ?, ?, ?)",
            (student, datetime.now().strftime("%Y-%m-%d %H:%M"), score, total, repr(topic_scores))
        )

def classify(pct):
    if pct >= 80:
        return "Yaxshi o‘zlashtirilgan", "Bu mavzuda murakkabroq topshiriqlarga o‘tish mumkin."
    if pct >= 50:
        return "Rivojlantirish kerak", "Asosiy tushunchalarni takrorlab, qo‘shimcha mashq bajaring."
    return "Qo‘shimcha yordam kerak", "Mavzuni boshidan takrorlash va o‘qituvchi bilan ishlash tavsiya etiladi."

def main():
    st.set_page_config(page_title="EDU AI", page_icon="🎓", layout="wide")
    init_db()
    st.title("🎓 EDU AI")
    st.caption("Har bir o‘quvchi uchun alohida ta’lim yo‘li")
    st.info("Namoyish prototipi: hozircha informatika fanidan 9 ta namunaviy savol va qoidaga asoslangan tavsiya mexanizmi ishlaydi. Bu hali o‘qitilgan ML modeli emas.")

    page = st.sidebar.radio("Bo‘lim", ["O‘quvchi diagnostikasi", "O‘qituvchi paneli", "Loyiha haqida"])

    if page == "O‘quvchi diagnostikasi":
        student = st.text_input("Ism yoki taxallus", placeholder="Masalan: O‘quvchi-01")
        st.subheader("Informatika bo‘yicha diagnostik test")
        st.write("Har bir savol uchun bitta javobni tanlang.")
        answers = {}
        with st.form("quiz_form"):
            for q in QUESTIONS:
                st.markdown(f"**{q['id']}. [{q['topic']}] {q['q']}**")
                answers[q["id"]] = st.radio(
                    "Javobni tanlang", q["opts"], key=f"q_{q['id']}",
                    index=None, label_visibility="collapsed"
                )
                st.divider()
            submitted = st.form_submit_button("Natijani tahlil qilish", type="primary")

        if submitted:
            if not student.strip():
                st.error("Iltimos, ism yoki taxallus kiriting.")
                return
            if any(v is None for v in answers.values()):
                st.warning("Iltimos, barcha savollarga javob bering.")
                return

            topic_total = defaultdict(int)
            topic_correct = defaultdict(int)
            wrong = []
            score = 0
            for q in QUESTIONS:
                topic_total[q["topic"]] += 1
                selected = q["opts"].index(answers[q["id"]])
                if selected == q["a"]:
                    score += 1
                    topic_correct[q["topic"]] += 1
                else:
                    wrong.append(q)

            topic_scores = {
                topic: round(topic_correct[topic] / count * 100)
                for topic, count in topic_total.items()
            }
            pct = round(score / len(QUESTIONS) * 100)
            save_attempt(student.strip(), score, len(QUESTIONS), topic_scores)

            st.success("Tahlil yakunlandi!")
            c1, c2, c3 = st.columns(3)
            c1.metric("To‘g‘ri javoblar", f"{score}/{len(QUESTIONS)}")
            c2.metric("Natija", f"{pct}%")
            c3.metric("Baholash", "Yuqori" if pct >= 80 else "O‘rta" if pct >= 50 else "Boshlang‘ich")

            st.subheader("Mavzular bo‘yicha tahlil")
            for topic, value in topic_scores.items():
                status, advice = classify(value)
                st.write(f"**{topic}: {value}% — {status}**")
                st.progress(value / 100)
                st.caption(advice)

            st.subheader("Siz uchun individual o‘quv rejasi")
            weakest = sorted(topic_scores.items(), key=lambda x: x[1])
            for topic, value in weakest:
                st.markdown(f"**{topic} ({value}%)**")
                related = [q for q in QUESTIONS if q["topic"] == topic]
                if value < 80:
                    for q in related:
                        st.write("• " + q["task"])
                else:
                    st.write("• Keyingi bosqichdagi murakkab masalalarni yeching.")

            if wrong:
                with st.expander("Xato javoblar va tushuntirishlar"):
                    for q in wrong:
                        st.markdown(f"**{q['topic']}: {q['q']}**")
                        st.write("To‘g‘ri javob: " + q["opts"][q["a"]])
                        st.caption(q["why"])

            st.caption("Eslatma: natija o‘quvchini qat’iy baholash yoki saralash uchun emas, o‘rganishga yordam berish uchun mo‘ljallangan.")

    elif page == "O‘qituvchi paneli":
        st.subheader("📊 O‘qituvchi paneli")
        with sqlite3.connect(DB_PATH) as con:
            rows = con.execute(
                "SELECT student, created_at, score, total, topic_scores FROM attempts ORDER BY id DESC"
            ).fetchall()
        if not rows:
            st.info("Hozircha natijalar yo‘q. Avval diagnostik testni bajaring.")
        else:
            st.metric("Jami urinishlar", len(rows))
            for student, date, score, total, topics in rows:
                with st.expander(f"{student} | {date} | {score}/{total}"):
                    st.write(f"Umumiy natija: {round(score/total*100)}%")
                    st.write("Mavzular kesimida:", topics)

    else:
        st.subheader("Loyiha haqida")
        st.write("EDU AI — o‘quvchining test javoblarini mavzular bo‘yicha tahlil qilib, keyingi o‘rganish uchun tavsiyalar beruvchi ta’lim prototipi.")
        st.markdown("""
        **Hozirgi prototip imkoniyatlari**
        - Informatika bo‘yicha diagnostik test
        - Mavzular kesimida natijalarni hisoblash
        - Xato javoblar uchun izoh
        - Individual mashq tavsiyalari
        - SQLite bazasida natijalarni saqlash
        - O‘qituvchi uchun natijalar paneli

        **Keyingi rivojlantirish bosqichlari**
        1. Fan va sinflar sonini ko‘paytirish.
        2. O‘quv materiallari bazasini yaratish.
        3. O‘quvchining oldingi natijalari asosida tavsiyalarni moslashtirish.
        4. Yetarli va sifatli ma’lumot yig‘ilgach, ML modelini sinash.
        """)

if __name__ == "__main__":
    main()
