"""
Ejecuta este script UNA SOLA VEZ para crear tu usuario administrador.
No guarda tu contraseña en texto plano en ningún lado, solo el hash en la BD.

Uso:
    python crear_admin.py
"""
import getpass
import MySQLdb
from werkzeug.security import generate_password_hash

# --- Datos de conexión (los mismos que en app.py) ---
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "kejoma_db"

# Debe ser EXACTAMENTE el mismo correo que pusiste en ADMIN_EMAIL_PERMITIDO
# dentro de app.py. Si no coincide, el login lo va a rechazar aunque la
# contraseña sea correcta.
ADMIN_EMAIL_PERMITIDO = "admin@kejoma.com"

def main():
    nombre = input("Tu nombre: ").strip()
    print(f"El correo debe ser exactamente: {ADMIN_EMAIL_PERMITIDO}")
    email = input(f"Tu correo [{ADMIN_EMAIL_PERMITIDO}]: ").strip() or ADMIN_EMAIL_PERMITIDO
    if email.lower() != ADMIN_EMAIL_PERMITIDO.lower():
        print("❌ Ese correo no coincide con ADMIN_EMAIL_PERMITIDO en app.py.")
        print("   Cambia esa constante en app.py o usa el correo indicado arriba.")
        return
    password = getpass.getpass("Elige tu contraseña de administrador: ")
    password2 = getpass.getpass("Repite la contraseña: ")

    if password != password2:
        print("❌ Las contraseñas no coinciden. Intenta de nuevo.")
        return

    if len(password) < 6:
        print("❌ Usa una contraseña de al menos 6 caracteres.")
        return

    password_hash = generate_password_hash(password)

    conn = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME)
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO administradores (nombre, email, password) VALUES (%s, %s, %s)",
            (nombre, email, password_hash),
        )
        conn.commit()
        print(f"✅ Administrador '{nombre}' creado correctamente. Ya puedes entrar en /login")
    except MySQLdb.IntegrityError:
        print("❌ Ese correo ya está registrado como administrador.")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
