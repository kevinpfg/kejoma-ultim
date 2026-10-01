import os
import secrets
import time
from datetime import date, timedelta
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, send_from_directory, abort
)
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ---------- Clave secreta ----------
# Se toma de la variable de entorno FLASK_SECRET_KEY si existe (recomendado
# en producción). Si no existe, se genera una aleatoria al arrancar el
# servidor: así nunca queda una clave débil/adivinable "de fábrica" y,
# de paso, cada reinicio invalida las sesiones viejas.
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)

# ---------- Sesiones seguras ----------
app.config["SESSION_COOKIE_HTTPONLY"] = True      # el JS del navegador no puede leer la cookie
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"      # evita que otros sitios reutilicen la cookie (CSRF)
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("FLASK_ENV") == "production"  # solo HTTPS en producción
app.config["PERMANENT_SESSION_LIFETIME"] = 60 * 60 * 2  # la sesión de administrador expira sola a las 2 horas

# ---------- Correo autorizado para entrar al panel admin ----------
# Solo este correo puede iniciar sesión como administrador, sin importar
# qué contraseña se escriba, ni aunque alguien intente registrar otro.
# Cámbialo por tu correo real antes de usar el proyecto.
ADMIN_EMAIL_PERMITIDO = "admin@kejoma.com"

# ---------- Conexión con MySQL / XAMPP ----------
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "kejoma_db"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

# ---------- Configuración de imágenes ----------
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
ALLOWED_EXT = {"png", "jpg", "jpeg", "webp", "gif"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def extension_valida(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


def guardar_imagen(archivo):
    """Guarda la imagen subida y devuelve el nombre de archivo, o None si no hay imagen."""
    if not archivo or archivo.filename == "":
        return None
    if not extension_valida(archivo.filename):
        flash("Formato de imagen no permitido (usa jpg, png, webp o gif).", "danger")
        return None
    nombre_seguro = secure_filename(archivo.filename)
    # Evita que dos productos con el mismo nombre de archivo se sobrescriban
    nombre_final = f"{os.urandom(4).hex()}_{nombre_seguro}"
    archivo.save(os.path.join(app.config["UPLOAD_FOLDER"], nombre_final))
    return nombre_final


# =========================================================
#  SEGURIDAD: cabeceras HTTP, CSRF y límite de intentos de login
# =========================================================

@app.after_request
def agregar_cabeceras_seguridad(respuesta):
    """Cabeceras básicas de seguridad para todas las respuestas."""
    respuesta.headers["X-Content-Type-Options"] = "nosniff"
    respuesta.headers["X-Frame-Options"] = "SAMEORIGIN"
    respuesta.headers["Referrer-Policy"] = "same-origin"
    return respuesta


def obtener_csrf_token():
    """Crea (si no existe) y devuelve el token CSRF de la sesión actual."""
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(24)
    return session["csrf_token"]


# Disponible en todas las plantillas como {{ csrf_token() }}
app.jinja_env.globals["csrf_token"] = obtener_csrf_token


@app.before_request
def validar_csrf_en_formularios():
    """Todo POST hecho desde un formulario propio (no JSON) debe traer el
    token CSRF que se generó al mostrar ese formulario. Esto evita que una
    página maliciosa externa pueda enviar cambios (precios, productos,
    ventas) usando la sesión de un administrador ya logueado."""
    if request.method == "POST":
        es_json = request.is_json or (request.content_type or "").startswith("application/json")
        if not es_json:
            token_form = request.form.get("csrf_token", "")
            token_sesion = session.get("csrf_token", "")
            if not token_sesion or not secrets.compare_digest(token_form, token_sesion):
                abort(400, description="Token de seguridad inválido o formulario expirado. Recarga la página e inténtalo de nuevo.")


# ---------- Límite de intentos de inicio de sesión (anti fuerza bruta) ----------
_INTENTOS_LOGIN = {}          # ip -> [cantidad_fallos, momento_ultimo_fallo]
_MAX_INTENTOS = 5
_BLOQUEO_SEGUNDOS = 60


def _ip_bloqueada(ip):
    fallos, ultimo = _INTENTOS_LOGIN.get(ip, (0, 0))
    if fallos >= _MAX_INTENTOS and (time.time() - ultimo) < _BLOQUEO_SEGUNDOS:
        return True
    if (time.time() - ultimo) >= _BLOQUEO_SEGUNDOS:
        _INTENTOS_LOGIN.pop(ip, None)
    return False


def _registrar_intento_fallido(ip):
    fallos, _ = _INTENTOS_LOGIN.get(ip, (0, 0))
    _INTENTOS_LOGIN[ip] = (fallos + 1, time.time())


def _limpiar_intentos(ip):
    _INTENTOS_LOGIN.pop(ip, None)


# ---------- Protección del panel admin ----------
def login_requerido(f):
    @wraps(f)
    def decorada(*args, **kwargs):
        if "admin_id" not in session:
            flash("Debes iniciar sesión para entrar al panel.", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorada


# =========================================================
#  TIENDA PÚBLICA — tu index.html + styles.css + script.js unidos
# =========================================================
@app.route("/")
def tienda():
    return render_template("tienda.html")


# Sirve las imágenes de tus productos (img max 1.webp, balon 1a.PNG, etc.)
# usando el MISMO nombre de archivo que ya tienes escrito en el HTML.
# Copia todas tus fotos dentro de la carpeta "imagenes_tienda/".
IMAGENES_TIENDA_DIR = os.path.join(app.root_path, "imagenes_tienda")


@app.route("/<path:nombre_archivo>")
def imagen_producto(nombre_archivo):
    return send_from_directory(IMAGENES_TIENDA_DIR, nombre_archivo)


# =========================================================
#  RAÍZ DEL PANEL — login clásico del admin (formulario propio)
# =========================================================
def credenciales_admin_validas(email, password):
    """Revisa correo + contraseña contra ADMIN_EMAIL_PERMITIDO y la BD.
    Devuelve el registro del administrador si es válido, o None."""
    email = (email or "").strip().lower()
    if not email or not password:
        return None
    if email != ADMIN_EMAIL_PERMITIDO.lower():
        return None
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM administradores WHERE email = %s", (email,))
    admin = cur.fetchone()
    cur.close()
    if admin and check_password_hash(admin["password"], password):
        return admin
    return None


@app.route("/login")
def login_url_vieja():
    # Por si tenías guardado el link viejo /login (ahora vive en /admin/login)
    return redirect(url_for("login"))


@app.route("/admin/login", methods=["GET", "POST"])
def login():
    ip = request.remote_addr or "desconocida"

    if request.method == "POST":
        if _ip_bloqueada(ip):
            flash(f"Demasiados intentos fallidos. Espera {_BLOQUEO_SEGUNDOS} segundos e inténtalo de nuevo.", "danger")
            return render_template("login.html")

        email = request.form.get("email", "")
        password = request.form.get("password", "")

        admin = credenciales_admin_validas(email, password)
        if admin:
            _limpiar_intentos(ip)
            session.clear()
            session.permanent = True
            session["admin_id"] = admin["id"]
            session["admin_nombre"] = admin["nombre"]
            flash("Bienvenido de nuevo.", "success")
            return redirect(url_for("admin_panel"))

        _registrar_intento_fallido(ip)
        flash("Correo o contraseña incorrectos.", "danger")

    return render_template("login.html")


# =========================================================
#  VERIFICACIÓN DESDE LA TIENDA — usada por el botón de login
#  de tu página pública para saber si eres tú (el admin)
# =========================================================
@app.route("/admin/verificar", methods=["POST"])
def verificar_admin_desde_tienda():
    ip = request.remote_addr or "desconocida"
    if _ip_bloqueada(ip):
        return {"admin": False, "bloqueado": True}

    datos = request.get_json(silent=True) or {}
    admin = credenciales_admin_validas(datos.get("correo"), datos.get("password"))
    if admin:
        _limpiar_intentos(ip)
        session.clear()
        session.permanent = True
        session["admin_id"] = admin["id"]
        session["admin_nombre"] = admin["nombre"]
        return {"admin": True}

    _registrar_intento_fallido(ip)
    return {"admin": False}


@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for("login"))


@app.errorhandler(400)
def solicitud_invalida(error):
    flash("Tu sesión de formulario expiró o no es válida. Intenta de nuevo.", "danger")
    return redirect(request.referrer or url_for("tienda"))


# =========================================================
#  PANTALLA "ADMIN" — aparece justo después de escribir la contraseña
# =========================================================
@app.route("/admin")
@login_requerido
def admin_panel():
    cur = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) AS total FROM productos")
    total_productos = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) AS total FROM ventas")
    total_ventas = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) AS total FROM productos WHERE stock = 0")
    productos_agotados = cur.fetchone()["total"]

    cur.execute("SELECT COALESCE(SUM(cantidad), 0) AS total FROM ventas")
    pedidos_realizados = cur.fetchone()["total"]

    cur.execute("SELECT COALESCE(SUM(total), 0) AS total FROM ventas")
    dinero_vendido = float(cur.fetchone()["total"])

    # Ventas de los últimos 14 días para la gráfica (día -> total vendido)
    cur.execute("""
        SELECT DATE(fecha_venta) AS dia, COALESCE(SUM(total), 0) AS total
        FROM ventas
        WHERE fecha_venta >= (CURDATE() - INTERVAL 13 DAY)
        GROUP BY DATE(fecha_venta)
        ORDER BY dia
    """)
    filas_grafica = cur.fetchall()
    cur.close()

    # Se completan los días sin ventas con 0, para que la gráfica no tenga huecos
    ventas_por_dia = {str(f["dia"]): float(f["total"]) for f in filas_grafica}
    etiquetas_grafica, datos_grafica = [], []
    hoy = date.today()
    for i in range(13, -1, -1):
        dia = hoy - timedelta(days=i)
        etiquetas_grafica.append(dia.strftime("%d/%m"))
        datos_grafica.append(ventas_por_dia.get(str(dia), 0))

    return render_template(
        "admin/dashboard.html",
        total_productos=total_productos,
        total_ventas=total_ventas,
        productos_agotados=productos_agotados,
        pedidos_realizados=pedidos_realizados,
        dinero_vendido=dinero_vendido,
        etiquetas_grafica=etiquetas_grafica,
        datos_grafica=datos_grafica,
    )


# =========================================================
#  PRODUCTOS — listado con imagen
# =========================================================
@app.route("/admin/productos")
@login_requerido
def lista_productos():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT p.id_producto, p.nombre, p.marca, p.precio, p.stock,
               p.estado, p.imagen, c.nombre_categoria
        FROM productos p
        INNER JOIN categorias c ON p.id_categoria = c.id_categoria
        ORDER BY p.id_producto DESC
    """)
    productos = cur.fetchall()
    cur.close()
    return render_template("admin/productos.html", productos=productos)


@app.route("/admin/productos/nuevo", methods=["GET", "POST"])
@login_requerido
def nuevo_producto():
    cur = mysql.connection.cursor()

    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        marca = request.form.get("marca", "").strip()
        precio = request.form["precio"]
        stock = request.form["stock"]
        id_categoria = request.form["id_categoria"]

        if not nombre or not precio or not stock or not id_categoria:
            flash("Completa todos los campos obligatorios.", "danger")
            return redirect(url_for("nuevo_producto"))

        try:
            if float(precio) < 0 or int(stock) < 0:
                flash("El precio y el stock no pueden ser negativos.", "danger")
                return redirect(url_for("nuevo_producto"))
        except ValueError:
            flash("Precio o stock inválidos.", "danger")
            return redirect(url_for("nuevo_producto"))

        imagen = guardar_imagen(request.files.get("imagen"))

        cur.execute("""
            INSERT INTO productos (nombre, marca, precio, stock, id_categoria, imagen)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nombre, marca, precio, stock, id_categoria, imagen))
        mysql.connection.commit()
        cur.close()
        flash("Producto creado correctamente.", "success")
        return redirect(url_for("lista_productos"))

    cur.execute("SELECT id_categoria, nombre_categoria FROM categorias ORDER BY nombre_categoria")
    categorias = cur.fetchall()
    cur.close()
    return render_template("admin/form_producto.html", categorias=categorias, producto=None)


@app.route("/admin/productos/editar/<int:id_producto>", methods=["GET", "POST"])
@login_requerido
def editar_producto(id_producto):
    cur = mysql.connection.cursor()

    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        marca = request.form.get("marca", "").strip()
        precio = request.form["precio"]
        stock = request.form["stock"]
        estado = request.form["estado"]
        id_categoria = request.form["id_categoria"]

        nueva_imagen = guardar_imagen(request.files.get("imagen"))

        if nueva_imagen:
            cur.execute("""
                UPDATE productos
                SET nombre=%s, marca=%s, precio=%s, stock=%s,
                    estado=%s, id_categoria=%s, imagen=%s
                WHERE id_producto=%s
            """, (nombre, marca, precio, stock, estado, id_categoria, nueva_imagen, id_producto))
        else:
            cur.execute("""
                UPDATE productos
                SET nombre=%s, marca=%s, precio=%s, stock=%s,
                    estado=%s, id_categoria=%s
                WHERE id_producto=%s
            """, (nombre, marca, precio, stock, estado, id_categoria, id_producto))

        mysql.connection.commit()
        cur.close()
        flash("Producto actualizado correctamente.", "success")
        return redirect(url_for("lista_productos"))

    cur.execute("SELECT * FROM productos WHERE id_producto = %s", (id_producto,))
    producto = cur.fetchone()
    cur.execute("SELECT id_categoria, nombre_categoria FROM categorias ORDER BY nombre_categoria")
    categorias = cur.fetchall()
    cur.close()

    if not producto:
        flash("Producto no encontrado.", "danger")
        return redirect(url_for("lista_productos"))

    return render_template("admin/form_producto.html", categorias=categorias, producto=producto)


@app.route("/admin/productos/desactivar/<int:id_producto>")
@login_requerido
def desactivar_producto(id_producto):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE productos SET estado = 'Inactivo' WHERE id_producto = %s", (id_producto,))
    mysql.connection.commit()
    cur.close()
    flash("Producto marcado como inactivo.", "success")
    return redirect(url_for("lista_productos"))


@app.route("/admin/productos/activar/<int:id_producto>")
@login_requerido
def activar_producto(id_producto):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE productos SET estado = 'Activo' WHERE id_producto = %s", (id_producto,))
    mysql.connection.commit()
    cur.close()
    flash("Producto activado.", "success")
    return redirect(url_for("lista_productos"))


@app.route("/admin/productos/eliminar/<int:id_producto>")
@login_requerido
def eliminar_producto(id_producto):
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM productos WHERE id_producto = %s", (id_producto,))
        mysql.connection.commit()
        flash("Producto eliminado.", "success")
    except Exception:
        mysql.connection.rollback()
        flash("No se puede eliminar: el producto tiene ventas asociadas. Desactívalo en su lugar.", "danger")
    finally:
        cur.close()
    return redirect(url_for("lista_productos"))


# =========================================================
#  MODIFICAR PRECIOS RÁPIDO (todos los productos en una sola tabla)
# =========================================================
@app.route("/admin/precios", methods=["GET", "POST"])
@login_requerido
def modificar_precios():
    cur = mysql.connection.cursor()

    if request.method == "POST":
        # Llegan varios campos precio_<id_producto> a la vez
        actualizados = 0
        for campo, valor in request.form.items():
            if campo.startswith("precio_") and valor.strip() != "":
                id_producto = campo.replace("precio_", "")
                try:
                    nuevo_precio = float(valor)
                    if nuevo_precio < 0:
                        continue
                except ValueError:
                    continue
                cur.execute(
                    "UPDATE productos SET precio = %s WHERE id_producto = %s",
                    (nuevo_precio, id_producto),
                )
                actualizados += 1
        mysql.connection.commit()
        cur.close()
        flash(f"Se actualizaron {actualizados} precios.", "success")
        return redirect(url_for("modificar_precios"))

    cur.execute("""
        SELECT p.id_producto, p.nombre, p.marca, p.precio, p.imagen, c.nombre_categoria
        FROM productos p
        INNER JOIN categorias c ON p.id_categoria = c.id_categoria
        ORDER BY c.nombre_categoria, p.nombre
    """)
    productos = cur.fetchall()
    cur.close()
    return render_template("admin/precios.html", productos=productos)


# =========================================================
#  VENTAS — registrar y ver productos vendidos
# =========================================================
@app.route("/admin/ventas/nueva", methods=["GET", "POST"])
@login_requerido
def nueva_venta():
    cur = mysql.connection.cursor()

    if request.method == "POST":
        id_producto = request.form["id_producto"]
        cantidad = request.form["cantidad"]

        cur.execute("SELECT stock, precio FROM productos WHERE id_producto = %s", (id_producto,))
        producto = cur.fetchone()

        try:
            cantidad = int(cantidad)
        except ValueError:
            cantidad = 0

        if not producto:
            flash("Producto no encontrado.", "danger")
        elif cantidad <= 0:
            flash("La cantidad debe ser mayor a cero.", "danger")
        elif cantidad > producto["stock"]:
            flash(f"No hay suficiente stock (disponible: {producto['stock']}).", "danger")
        else:
            total = float(producto["precio"]) * cantidad
            cur.execute(
                "INSERT INTO ventas (id_producto, cantidad, total) VALUES (%s, %s, %s)",
                (id_producto, cantidad, total),
            )
            cur.execute(
                "UPDATE productos SET stock = stock - %s WHERE id_producto = %s",
                (cantidad, id_producto),
            )
            mysql.connection.commit()
            flash("Venta registrada y stock actualizado.", "success")
            cur.close()
            return redirect(url_for("ventas"))

    cur.execute("""
        SELECT id_producto, nombre, marca, precio, stock
        FROM productos
        WHERE estado = 'Activo'
        ORDER BY nombre
    """)
    productos = cur.fetchall()
    cur.close()
    return render_template("admin/nueva_venta.html", productos=productos)


@app.route("/admin/ventas/eliminar/<int:id_venta>")
@login_requerido
def eliminar_venta(id_venta):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM ventas WHERE id_venta = %s", (id_venta,))
    mysql.connection.commit()
    cur.close()
    flash("Venta eliminada del historial.", "success")
    return redirect(url_for("ventas"))


# =========================================================
#  REPORTE DE VENTAS (consulta multitabla, opcional)
# =========================================================
@app.route("/admin/ventas")
@login_requerido
def ventas():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT v.id_venta, p.nombre, p.imagen, c.nombre_categoria, v.cantidad,
               p.precio, (v.cantidad * p.precio) AS total, v.fecha_venta
        FROM ventas v
        INNER JOIN productos p ON v.id_producto = p.id_producto
        INNER JOIN categorias c ON p.id_categoria = c.id_categoria
        ORDER BY v.fecha_venta DESC
    """)
    lista_ventas = cur.fetchall()
    cur.close()
    return render_template("admin/ventas.html", ventas=lista_ventas)


if __name__ == "__main__":
    app.run(debug=True)
