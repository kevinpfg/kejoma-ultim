# KEJOMA — Tienda + Panel Admin, todo en un mismo proyecto Flask

Ahora tu tienda pública y tu panel de administración viven en el **mismo
servidor Flask**. Ya no son dos cosas separadas.

- `http://127.0.0.1:5000/` → tu tienda KEJOMA (tu index.html + styles.css +
  script.js originales, unidos en `templates/tienda.html`, sin cambiar tu
  diseño ni tu funcionamiento).
- `http://127.0.0.1:5000/admin/login` → tu panel de administración (solo tú
  entras, con tu correo y contraseña).

## 1. Base de datos
Igual que antes: pega `schema.sql` completo en phpMyAdmin (pestaña SQL). Crea
`kejoma_db` con tus 104 productos reales, categorías, ventas y tu tabla de
administradores.

## 2. Tu correo de administrador
En `app.py`:
```python
ADMIN_EMAIL_PERMITIDO = "admin@kejoma.com"
```
Cámbialo por el correo que quieras usar para entrar al panel.

## 3. Instalar y preparar
```
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python crear_admin.py
```

## 4. Poner tus fotos de productos
Tu `index.html` original hace referencia a imágenes por su nombre de archivo
(`img max 1.webp`, `balon 1a.PNG`, etc.), todas sueltas en la misma carpeta
del proyecto. Para que se vean en la tienda, copia todas esas fotos dentro de
la carpeta:
```
kejoma_flask/imagenes_tienda/
```
usando EXACTAMENTE los mismos nombres que ya tienes en el HTML (respetando
mayúsculas/minúsculas). Flask las va a servir automáticamente con esos
mismos nombres, sin que tengas que tocar ni una línea del HTML.

## 5. Ejecutar todo junto
```
python app.py
```
- Tienda: `http://127.0.0.1:5000/`
- Panel admin: `http://127.0.0.1:5000/admin/login`

Desde el panel puedes ver "Ver tienda" en la barra superior para abrir tu
página pública en una pestaña nueva, y desde el login del panel hay un enlace
para volver a la tienda.

## 6. Qué hace cada parte
**Tienda pública (`/`)**: exactamente tu página KEJOMA de siempre — carrito,
buscador, filtros, carrusel, checkout — todo tal cual estaba. Por ahora sigue
mostrando los productos que están escritos directamente en el HTML (no lee
todavía la base de datos).

**Panel admin (`/admin/...`)**: trabaja sobre la base de datos MySQL —
productos, precios, ventas — de forma independiente.

## 7. Siguiente paso opcional: que la tienda lea los precios de la base de datos
Ahora mismo son dos fuentes de información: el HTML tiene los precios escritos
a mano, y la base de datos tiene los suyos (que puedes editar en el panel).
Si cambias un precio en el panel, todavía **no se refleja solo** en la tienda
pública, porque la tienda no consulta la base de datos.

Si quieres que sí se conecten (que al cambiar un precio en `/admin/precios`
se actualice automáticamente lo que ve el cliente), el siguiente paso sería
que `script.js` pida los precios a Flask (por ejemplo a una ruta
`/api/productos`) en vez de tenerlos fijos en el HTML. Es un cambio más
grande porque tocaría la forma en que se pintan los productos; dímelo cuando
quieras que lo hagamos.

## Seguridad
- Cambia `app.secret_key` en `app.py` por una clave larga y aleatoria.
- Nunca se guarda tu contraseña real, solo su hash (Werkzeug).
