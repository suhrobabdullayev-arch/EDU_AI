# EDU AI — ishlaydigan boshlang‘ich prototip

## Ishga tushirish
1. Kompyuterga Python 3.10 yoki undan yangiroq versiyasini o‘rnating.
2. ZIP faylni oching.
3. Shu papkada terminal/CMD oching.
4. Quyidagi buyruqlarni bajaring:

```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

Keyin:
```bash
pip install -r requirements.txt
streamlit run app.py
```

Brauzerda EDU AI ochiladi. Odatda manzil: http://localhost:8501

## Prototip nimalarni bajaradi?
- Informatika fanidan 9 ta namunaviy savol beradi.
- Javoblarni mavzular kesimida tahlil qiladi.
- Xato javoblar uchun izoh ko‘rsatadi.
- Individual mashq tavsiyalarini shakllantiradi.
- Natijalarni lokal SQLite bazasiga saqlaydi.
- O‘qituvchi panelida urinishlarni ko‘rsatadi.

## Muhim texnik izoh
Bu versiya ishlaydigan MVP bo‘lib, tavsiyalar qoidaga asoslangan. U o‘qitilgan sun’iy intellekt yoki ML modeli emas. Tanlovda buni ochiq ayting. Keyingi bosqichda o‘quvchi natijalari va o‘quv kontenti asosida tavsiya mexanizmini sinovdan o‘tkazib, validatsiyalangan ML modeliga o‘tish mumkin.

## Maxfiylik
- Demo uchun haqiqiy o‘quvchi F.I.Sh., telefon raqami yoki boshqa shaxsiy ma’lumotlarni kiritmang.
- Namoyishda taxalluslardan foydalaning.
- Ma’lumotlar kompyuterdagi `edu_ai.db` faylida saqlanadi.
