import os
from functools import wraps
from urllib.parse import quote

from flask import (Flask, render_template, redirect, url_for, request,
                   flash, abort, Response)
from flask_wtf import CSRFProtect
from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user)
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from psycopg2 import errors as pg_errors

from conexion import probar_conexion, inicializar_bd
from forms.solicitud_form import SolicitudForm
from forms.cliente_form import ClienteForm
from forms.pago_form import PagoForm
from forms.login_form import LoginForm
from forms.usuario_form import UsuarioForm
from models import (Usuario, listar_servicios, listar_solicitudes,
                    obtener_solicitud, crear_solicitud, actualizar_solicitud,
                    eliminar_solicitud, resumen_por_servicio,
                    listar_clientes, listar_clientes_simple, obtener_cliente,
                    crear_cliente, actualizar_cliente, eliminar_cliente,
                    solicitudes_de_cliente, total_clientes,
                    crear_pago, listar_pagos, obtener_pago, obtener_comprobante,
                    actualizar_estado_pago, total_pagos_pendientes)

app = Flask(__name__)

# La clave real va en el archivo .env (no se sube a GitHub).
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "clave-solo-para-desarrollo")

# Protección CSRF global para todos los formularios de la app
csrf = CSRFProtect(app)

# Límite de subida: 6 MB (la foto del comprobante se valida en 5 MB)
app.config["MAX_CONTENT_LENGTH"] = 6 * 1024 * 1024
MAX_COMPROBANTE = 5 * 1024 * 1024

# Datos del negocio (se muestran en pagos, factura y WhatsApp)
NEGOCIO = {
    "nombre": "Leggy",
    "banco": "Banco Pichincha",
    "cuenta": "2213632740",
    "titular": "Leslye Valencia",
    "whatsapp": os.environ.get("WHATSAPP_NUMERO", "593999231755"),
}


@app.context_processor
def datos_globales():
    """Variables disponibles en todas las plantillas."""
    def wa_link(texto):
        return f"https://wa.me/{NEGOCIO['whatsapp']}?text={quote(texto)}"
    return {"negocio": NEGOCIO, "wa_link": wa_link}


@app.template_filter("numero_factura")
def numero_factura(id_pago):
    return f"FAC-{int(id_pago):06d}"


@app.template_filter("clase_estado")
def clase_estado(estado):
    return {"pendiente": "warning text-dark", "verificado": "success",
            "rechazado": "danger"}.get(estado, "secondary")

# ---------------------------------------------------------------
# Flask-Login
# ---------------------------------------------------------------
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Inicia sesión para acceder a esta página."
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    """Recupera el usuario desde PostgreSQL a partir del id guardado en la sesión."""
    return Usuario.obtener_por_id(user_id)


def destino_seguro(destino):
    """Solo permite redirigir a rutas internas (evita open redirect)."""
    if destino and destino.startswith("/") and not destino.startswith("//"):
        return destino
    return None


def admin_required(vista):
    """Solo la administradora (ADMIN_USUARIO). Los demás reciben 403."""
    @wraps(vista)
    @login_required
    def envoltura(*args, **kwargs):
        if not current_user.es_admin:
            abort(403)
        return vista(*args, **kwargs)
    return envoltura


def asegurar_admin():
    """Crea la cuenta admin si hay ADMIN_USUARIO y ADMIN_PASSWORD y aún no existe."""
    nombre = os.environ.get("ADMIN_USUARIO", "").strip()
    clave = os.environ.get("ADMIN_PASSWORD", "")
    if nombre and clave and Usuario.obtener_por_usuario(nombre) is None:
        Usuario.crear(nombre, generate_password_hash(clave))


def detectar_imagen(datos):
    """Devuelve el tipo MIME según los primeros bytes (no confía en el nombre)."""
    if datos.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if datos.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if datos[:4] == b"RIFF" and datos[8:12] == b"WEBP":
        return "image/webp"
    return None


def texto_pago_whatsapp(pago):
    return (f"Hola Leggy, acabo de pagar por transferencia.\n"
            f"Factura: {numero_factura(pago['id_pago'])}\n"
            f"Servicio: {pago['servicio']}\n"
            f"Monto: ${pago['monto']:.2f}\n"
            f"Código de transferencia: {pago['codigo_transferencia']}\n"
            f"Te adjunto aquí la foto de mi comprobante.")


def pago_permitido(id_pago):
    """Devuelve el pago si pertenece al usuario actual o es admin; si no, 404."""
    pago = obtener_pago(id_pago)
    if pago is None or not (current_user.es_admin or pago["id_usuario"] == current_user.id):
        abort(404)
    return pago


# ---------------------------------------------------------------
# Datos de Servicios: galería de imágenes (estáticas) y el nombre del
# servicio, que coincide con la tabla servicios de PostgreSQL.
# ---------------------------------------------------------------
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


def cargar_opciones(form):
    """Llena los <select> de cliente y tipo con datos de PostgreSQL."""
    servicios = listar_servicios()
    form.tipo.choices = [("", "Seleccione")] + [
        (str(s["id_servicio"]), s["nombre"]) for s in servicios
    ]
    form.cliente.choices = [("", "Seleccione")] + [
        (str(c["id_cliente"]), c["nombre"]) for c in listar_clientes_simple()
    ]
    return servicios


# ---------------------------------------------------------------
# Páginas públicas
# ---------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


def precios_por_nombre():
    """Precios de la tabla servicios {nombre: precio}; vacío si la BD no responde."""
    try:
        return {s["nombre"]: s["precio"] for s in listar_servicios()}
    except psycopg2.Error:
        return {}


@app.route("/servicios")
def servicios():
    precios = precios_por_nombre()
    lista = [dict(s, precio=precios.get(s["tipo_solicitud"])) for s in servicios_data]
    return render_template("servicios.html", servicios=lista)


@app.route("/contacto")
def contacto():
    return render_template("contacto.html")


# ---------------------------------------------------------------
# Autenticación
# ---------------------------------------------------------------
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = UsuarioForm()
    if form.validate_on_submit():
        nombre_usuario = form.usuario.data.strip()

        if Usuario.obtener_por_usuario(nombre_usuario):
            form.usuario.errors.append("Ese usuario ya existe, elige otro.")
        else:
            # La contraseña se guarda siempre como hash
            password_hash = generate_password_hash(form.password.data)
            try:
                Usuario.crear(nombre_usuario, password_hash)
            except pg_errors.UniqueViolation:  # UNIQUE en usuarios.usuario
                form.usuario.errors.append("Ese usuario ya existe, elige otro.")
            else:
                flash("Cuenta creada correctamente. Ya puedes iniciar sesión.", "success")
                return redirect(url_for("login"))

    return render_template("registro.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.obtener_por_usuario(form.usuario.data.strip())

        # Se compara contra el hash, nunca contra texto plano
        if usuario and check_password_hash(usuario.password, form.password.data):
            login_user(usuario)
            flash(f"¡Bienvenida/o, {usuario.usuario}!", "success")
            return redirect(destino_seguro(request.args.get("next")) or url_for("dashboard"))

        flash("Usuario o contraseña incorrectos.", "danger")

    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    # Las clientas/clientes van a "Mis pagos"; el panel es solo para la administradora
    if not current_user.es_admin:
        return redirect(url_for("mis_pagos"))
    resumen = resumen_por_servicio()
    total = sum(fila["total"] for fila in resumen)
    return render_template("dashboard.html", resumen=resumen, total=total,
                           clientes=total_clientes(),
                           pendientes=total_pagos_pendientes())


# ---------------------------------------------------------------
# Clientes (CRUD completo sobre PostgreSQL) - rutas protegidas
# ---------------------------------------------------------------
@app.route("/clientes", methods=["GET", "POST"])
@admin_required
def clientes():
    form = ClienteForm()

    # CREAR: formulario -> validación -> INSERT
    if form.validate_on_submit():
        crear_cliente(form.nombre.data.strip(),
                      form.telefono.data.strip() or None,
                      form.correo.data.strip() or None)
        flash("Cliente registrado correctamente.", "success")
        return redirect(url_for("clientes"))

    # LEER: SELECT con JOIN (y WHERE si se busca)
    busqueda = request.args.get("q", "").strip()
    return render_template("clientes.html", form=form,
                           clientes=listar_clientes(busqueda), busqueda=busqueda)


@app.route("/clientes/<int:id_cliente>")
@admin_required
def detalle_cliente(id_cliente):
    """Información relacionada: las solicitudes de un cliente (JOIN)."""
    cliente = obtener_cliente(id_cliente)
    if cliente is None:
        abort(404)
    return render_template("cliente_detalle.html", cliente=cliente,
                           solicitudes=solicitudes_de_cliente(id_cliente))


@app.route("/clientes/editar/<int:id_cliente>", methods=["GET", "POST"])
@admin_required
def editar_cliente(id_cliente):
    registro = obtener_cliente(id_cliente)
    if registro is None:
        abort(404)

    form = ClienteForm()
    form.submit.label.text = "Guardar cambios"

    if request.method == "GET":
        form.nombre.data = registro["nombre"]
        form.telefono.data = registro["telefono"]
        form.correo.data = registro["correo"]

    # ACTUALIZAR: UPDATE ... WHERE id
    if form.validate_on_submit():
        actualizar_cliente(id_cliente,
                           form.nombre.data.strip(),
                           form.telefono.data.strip() or None,
                           form.correo.data.strip() or None)
        flash("Cliente actualizado correctamente.", "success")
        return redirect(url_for("clientes"))

    return render_template("formulario_cliente.html", form=form, cliente=registro)


@app.route("/clientes/eliminar/<int:id_cliente>", methods=["POST"])
@admin_required
def eliminar_cliente_ruta(id_cliente):
    # ELIMINAR: DELETE ... WHERE id (solo por POST, con token CSRF)
    try:
        if eliminar_cliente(id_cliente):
            flash("Cliente eliminado.", "success")
        else:
            flash("El cliente ya no existe.", "warning")
    except pg_errors.ForeignKeyViolation:
        flash("No se puede eliminar: el cliente tiene solicitudes registradas. "
              "Elimina primero sus solicitudes.", "danger")
    return redirect(url_for("clientes"))


# ---------------------------------------------------------------
# Solicitudes (CRUD completo sobre PostgreSQL) - rutas protegidas
# ---------------------------------------------------------------
@app.route("/solicitudes", methods=["GET", "POST"])
@admin_required
def solicitudes():
    form = SolicitudForm()
    servicios_bd = cargar_opciones(form)

    # Si se llega desde el botón "Encargar..." de Servicios (?tipo=...),
    # se preselecciona la categoría (solo en GET).
    if request.method == "GET":
        tipo_nombre = request.args.get("tipo")
        for s in servicios_bd:
            if s["nombre"] == tipo_nombre:
                form.tipo.data = str(s["id_servicio"])

    # CREAR: formulario -> validación -> INSERT
    if form.validate_on_submit():
        crear_solicitud(int(form.cliente.data),
                        int(form.tipo.data),
                        form.descripcion.data.strip())
        flash("Solicitud registrada correctamente.", "success")
        return redirect(url_for("solicitudes"))

    # LEER: SELECT con JOIN de 3 tablas (con búsqueda opcional usando WHERE)
    busqueda = request.args.get("q", "").strip()
    return render_template("solicitudes.html", form=form,
                           solicitudes=listar_solicitudes(busqueda),
                           busqueda=busqueda,
                           hay_clientes=len(form.cliente.choices) > 1)


@app.route("/solicitudes/editar/<int:id_solicitud>", methods=["GET", "POST"])
@admin_required
def editar_solicitud(id_solicitud):
    registro = obtener_solicitud(id_solicitud)
    if registro is None:
        abort(404)

    form = SolicitudForm()
    cargar_opciones(form)
    form.submit.label.text = "Guardar cambios"

    # Carga los datos actuales dentro del formulario
    if request.method == "GET":
        form.cliente.data = str(registro["id_cliente"])
        form.descripcion.data = registro["descripcion"]
        form.tipo.data = str(registro["id_servicio"])

    # ACTUALIZAR: UPDATE ... WHERE id
    if form.validate_on_submit():
        actualizar_solicitud(id_solicitud,
                             int(form.cliente.data),
                             int(form.tipo.data),
                             form.descripcion.data.strip())
        flash("Solicitud actualizada correctamente.", "success")
        return redirect(url_for("solicitudes"))

    return render_template("formulario_solicitud.html", form=form,
                           solicitud=registro, hay_clientes=True)


@app.route("/solicitudes/eliminar/<int:id_solicitud>", methods=["POST"])
@admin_required
def eliminar(id_solicitud):
    # ELIMINAR: DELETE ... WHERE id (solo por POST, con token CSRF)
    if eliminar_solicitud(id_solicitud):
        flash("Solicitud eliminada.", "success")
    else:
        flash("La solicitud ya no existe.", "warning")
    return redirect(url_for("solicitudes"))


# ---------------------------------------------------------------
# Encargos y pagos por transferencia
# ---------------------------------------------------------------
@app.route("/encargar/<slug>")
def encargar(slug):
    """Paso a paso para el cliente: foto por WhatsApp -> pago o más detalles."""
    servicio = next((s for s in servicios_data if s["slug"] == slug), None)
    if servicio is None:
        abort(404)
    precio = precios_por_nombre().get(servicio["tipo_solicitud"])
    return render_template("encargar.html", servicio=servicio, precio=precio)


@app.route("/pagar", methods=["GET", "POST"])
@login_required
def pagar():
    form = PagoForm()
    servicios_bd = listar_servicios()
    form.servicio.choices = [("", "Seleccione")] + [
        (str(s["id_servicio"]), s["nombre"]) for s in servicios_bd
    ]

    if request.method == "GET":
        for s in servicios_bd:
            if s["nombre"] == request.args.get("servicio"):
                form.servicio.data = str(s["id_servicio"])

    # El monto sale del precio guardado en la tabla servicios (no lo escribe el cliente)
    precios = {str(s["id_servicio"]): f"{s['precio']:.2f}" for s in servicios_bd}

    if form.validate_on_submit():
        monto = next(s["precio"] for s in servicios_bd
                     if str(s["id_servicio"]) == form.servicio.data)
        imagen = form.comprobante.data.read()
        tipo = detectar_imagen(imagen)
        if len(imagen) > MAX_COMPROBANTE:
            form.comprobante.errors.append("La imagen supera los 5 MB.")
        elif tipo is None:
            form.comprobante.errors.append("El archivo no es una imagen válida.")
        elif monto <= 0:
            flash("Este servicio aún no tiene precio. Escríbeme por WhatsApp.", "warning")
        else:
            try:
                id_pago = crear_pago(current_user.id, int(form.servicio.data),
                                     monto,
                                     form.codigo.data.strip().upper(),
                                     imagen, tipo)
            except pg_errors.UniqueViolation:
                form.codigo.errors.append("Ese código de transferencia ya fue registrado.")
            else:
                return redirect(url_for("pago_enviado", id_pago=id_pago))

    return render_template("pagar.html", form=form, precios=precios)


@app.route("/pago/<int:id_pago>/enviado")
@login_required
def pago_enviado(id_pago):
    pago = pago_permitido(id_pago)
    return render_template("pago_enviado.html", pago=pago,
                           mensaje_wa=texto_pago_whatsapp(pago))


@app.route("/factura/<int:id_pago>")
@login_required
def factura(id_pago):
    pago = pago_permitido(id_pago)
    return render_template("factura.html", pago=pago,
                           mensaje_wa=texto_pago_whatsapp(pago))


@app.route("/mis-pagos")
@login_required
def mis_pagos():
    return render_template("mis_pagos.html", pagos=listar_pagos(current_user.id))


@app.route("/pago/<int:id_pago>/comprobante")
@login_required
def comprobante(id_pago):
    """Muestra la foto del comprobante (solo su dueño o la administradora)."""
    fila = obtener_comprobante(id_pago)
    if fila is None or not (current_user.es_admin or fila["id_usuario"] == current_user.id):
        abort(404)
    respuesta = Response(bytes(fila["comprobante"]), mimetype=fila["comprobante_tipo"])
    respuesta.headers["Cache-Control"] = "private, no-store"
    respuesta.headers["X-Content-Type-Options"] = "nosniff"
    return respuesta


@app.route("/admin/pagos")
@admin_required
def admin_pagos():
    return render_template("admin_pagos.html", pagos=listar_pagos())


@app.route("/admin/pagos/<int:id_pago>/estado", methods=["POST"])
@admin_required
def cambiar_estado_pago(id_pago):
    estado = request.form.get("estado")
    if estado not in ("verificado", "rechazado", "pendiente"):
        abort(400)
    if actualizar_estado_pago(id_pago, estado):
        flash(f"Pago #{id_pago} marcado como {estado}.", "success")
    else:
        flash("El pago no existe.", "warning")
    return redirect(url_for("admin_pagos"))


# ---------------------------------------------------------------
# Errores
# ---------------------------------------------------------------
@app.errorhandler(psycopg2.Error)
def error_base_datos(error):
    app.logger.error("Error de PostgreSQL: %s", error)
    return render_template("error.html"), 500


@app.errorhandler(403)
def error_403(error):
    return render_template("error.html", titulo="Acceso restringido",
                           mensaje="Esta sección es solo para la administradora."), 403


@app.errorhandler(404)
def error_404(error):
    return render_template("error.html", titulo="Página no encontrada",
                           mensaje="Lo que buscas no existe o no tienes acceso."), 404


@app.errorhandler(413)
def error_413(error):
    return render_template("error.html", titulo="Imagen demasiado pesada",
                           mensaje="La foto no puede superar los 5 MB."), 413


def preparar_bd():
    """Crea las tablas (si faltan) y la cuenta admin (si se configuró)."""
    inicializar_bd()
    asegurar_admin()


# En Render INIT_DB=1 prepara la base al arrancar (esquema repetible).
if os.environ.get("INIT_DB") == "1":
    preparar_bd()


if __name__ == "__main__":
    if probar_conexion():
        print("Conexión a PostgreSQL correcta.")
        preparar_bd()
    app.run(debug=True)
