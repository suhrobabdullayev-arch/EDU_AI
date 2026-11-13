
from getpass import getpass
import auth

# Ma'lumotlar bazasini tekshirish
auth.initialize_auth()

# Administrator mavjudligini tekshirish
users = auth.get_all_users()

if any(user["role"] == "admin" for user in users):
    print("Administrator hisobi allaqachon mavjud.")
    raise SystemExit

print("=== EDU AI | ADMINISTRATOR YARATISH ===")

username = input("Administrator logini: ").strip()
full_name = input("Ism-familiyasi: ").strip()

password = getpass("Parol kiriting: ")
confirm_password = getpass("Parolni qayta kiriting: ")

if password != confirm_password:
    print("Xatolik: parollar bir xil emas!")
    raise SystemExit

try:
    auth.create_user(
        username=username,
        full_name=full_name,
        password=password,
        role="admin"
    )

    print("\nAdministrator muvaffaqiyatli yaratildi!")
    print("Endi ushbu login orqali platformaga kirishingiz mumkin.")

except ValueError as error:
    print(f"\nXatolik: {error}")
