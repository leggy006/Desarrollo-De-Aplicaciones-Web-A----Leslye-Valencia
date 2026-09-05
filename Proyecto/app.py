import os
import sqlite3

from flask import Flask, render_template, redirect, url_for, request
from flask_wtf import CSRFProtect

from forms.solicitud_form import SolicitudForm

app = Flask(__name__)

# Necesaria para CSRF y para que Flask-WTF funcione correctamente.
# En un proyecto real esto debería venir de una variable de entorno.
app.config["SECRET_KEY"] = "cambia-esta-clave-por-una-mas-segura"

# Protección CSRF global para todos los formularios de la app
csrf = CSRFProtect(app)

# ---------------------------------------------------------------
# Configuración de la base de datos SQLite
# ---------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "arte_en_cada_trazo.db")


def get_db_connection():
    """Abre y devuelve una conexión a la base de datos SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Crea la carpeta data/ y la tabla solicitudes si no existen."""
    os.makedirs(DATA_DIR, exist_ok=True)

    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS solicitudes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            tipo TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# Datos de Servicios: cada uno con su galería de imágenes y el tipo de
# solicitud asociado (para precargar el formulario de Solicitudes).
servicios_data = [
    {
        "slug": "retratos",
        "titulo": "Retratos personalizados",
        "descripcion": "Retratos únicos personalizados a partir de tus fotos favoritas.",
        "imagenes": ["retra1.png", "retra2.png", "retra3.png", "retra4.png", "retra5.png", "retra6.png"],
        "tipo_solicitud": "Retrato personalizado"
    },
    {
        "slug": "caricaturas",
        "titulo": "Caricaturas a lápiz",
        "descripcion": "Creaciones artísticas detalladas realizadas a mano.",
        "imagenes": ["cari1.png"],
        "tipo_solicitud": "Caricatura a lápiz"
    },
    {
        "slug": "pinturas",
        "titulo": "Pinturas personalizadas",
        "descripcion": "Diseños digitales personalizados para cualquier ocasión.",
        "imagenes": ["pint1.png", "pint2.png", "pint3.png", "pint4.png"],
        "tipo_solicitud": "Pintura personalizada"
    }
]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/servicios")
def servicios():
    return render_template("servicios.html", servicios=servicios_data)


@app.route("/contacto")
def contacto():
    return render_template("contacto.html")


@app.route("/solicitudes", methods=["GET", "POST"])
def solicitudes():
    form = SolicitudForm()

    # Si se llega desde el botón "Encargar..." de Servicios (?tipo=...),
    # se precarga la categoría en el formulario (solo en GET).
    if request.method == "GET":
        tipo_preseleccionado = request.args.get("tipo")
        if tipo_preseleccionado:
            form.tipo.data = tipo_preseleccionado

    # 1. Formulario -> 2. Validación (Flask-WTF/WTForms)
    if form.validate_on_submit():
        nombre = form.nombre.data.strip()
        descripcion = form.descripcion.data.strip()
        tipo = form.tipo.data

        # 3. INSERT: se guarda en SQLite solo si el formulario es válido
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO solicitudes (nombre, descripcion, tipo) VALUES (?, ?, ?)",
            (nombre, descripcion, tipo)
        )
        conn.commit()
        conn.close()

        # Patrón POST/Redirect/GET: evita reenvíos duplicados al refrescar
        return redirect(url_for("solicitudes"))

    # 4. SELECT: se recuperan todos los registros almacenados
    conn = get_db_connection()
    filas = conn.execute(
        "SELECT id, nombre, descripcion, tipo FROM solicitudes ORDER BY id DESC"
    ).fetchall()
    conn.close()

    # 5. Jinja2: se envían los registros a la plantilla para mostrarlos en una tabla
    return render_template("solicitudes.html", form=form, solicitudes=filas)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
