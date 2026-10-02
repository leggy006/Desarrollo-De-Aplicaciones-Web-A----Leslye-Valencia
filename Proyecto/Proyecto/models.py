"""Acceso a datos (PostgreSQL) y modelo de usuario para Flask-Login."""
import os

import psycopg2
from flask_login import UserMixin

from conexion import consultar, ejecutar


# ---------------------------------------------------------------
# Usuarios
# ---------------------------------------------------------------
class Usuario(UserMixin):
    """Usuario compatible con Flask-Login (UserMixin aporta get_id, etc.)."""

    def __init__(self, id, usuario, password):
        self.id = id
        self.usuario = usuario
        self.password = password  # hash, nunca texto plano

    @property
    def es_admin(self):
        """Es administradora si su usuario coincide con ADMIN_USUARIO (.env / Render)."""
        admin = os.environ.get("ADMIN_USUARIO", "").strip().lower()
        return bool(admin) and self.usuario.lower() == admin

    @staticmethod
    def _desde_fila(fila):
        if fila is None:
            return None
        return Usuario(fila["id"], fila["usuario"], fila["password"])

    @staticmethod
    def obtener_por_id(user_id):
        fila = consultar(
            "SELECT id, usuario, password FROM usuarios WHERE id = %s",
            (user_id,), uno=True)
        return Usuario._desde_fila(fila)

    @staticmethod
    def obtener_por_usuario(nombre_usuario):
        fila = consultar(
            "SELECT id, usuario, password FROM usuarios WHERE usuario = %s",
            (nombre_usuario,), uno=True)
        return Usuario._desde_fila(fila)

    @staticmethod
    def crear(nombre_usuario, password_hash):
        ejecutar("INSERT INTO usuarios (usuario, password) VALUES (%s, %s)",
                 (nombre_usuario, password_hash))


# ---------------------------------------------------------------
# Servicios (tabla relacionada)
# ---------------------------------------------------------------
def listar_servicios():
    return consultar("SELECT id_servicio, nombre, precio FROM servicios ORDER BY id_servicio")


# ---------------------------------------------------------------
# Clientes: SELECT / INSERT / UPDATE / DELETE
# ---------------------------------------------------------------
def listar_clientes(busqueda=""):
    """SELECT de clientes con el total de solicitudes de cada uno (JOIN)."""
    sql = """
        SELECT c.id_cliente, c.nombre, c.telefono, c.correo,
               COUNT(s.id_solicitud) AS total_solicitudes
        FROM clientes c
        LEFT JOIN solicitudes s ON s.id_cliente = c.id_cliente
    """
    params = ()
    if busqueda:
        sql += " WHERE c.nombre ILIKE %s OR c.correo ILIKE %s"
        patron = f"%{busqueda}%"
        params = (patron, patron)
    sql += " GROUP BY c.id_cliente, c.nombre, c.telefono, c.correo ORDER BY c.id_cliente DESC"
    return consultar(sql, params)


def listar_clientes_simple():
    return consultar("SELECT id_cliente, nombre FROM clientes ORDER BY nombre")


def obtener_cliente(id_cliente):
    return consultar(
        "SELECT id_cliente, nombre, telefono, correo FROM clientes WHERE id_cliente = %s",
        (id_cliente,), uno=True)


def crear_cliente(nombre, telefono, correo):
    ejecutar("INSERT INTO clientes (nombre, telefono, correo) VALUES (%s, %s, %s)",
             (nombre, telefono, correo))


def actualizar_cliente(id_cliente, nombre, telefono, correo):
    ejecutar("UPDATE clientes SET nombre = %s, telefono = %s, correo = %s "
             "WHERE id_cliente = %s",
             (nombre, telefono, correo, id_cliente))


def eliminar_cliente(id_cliente):
    return ejecutar("DELETE FROM clientes WHERE id_cliente = %s", (id_cliente,))


def solicitudes_de_cliente(id_cliente):
    """Consulta relacionada: solicitudes de un cliente (JOIN con servicios)."""
    return consultar("""
        SELECT s.id_solicitud, s.descripcion, sv.nombre AS tipo
        FROM solicitudes s
        INNER JOIN servicios sv ON s.id_servicio = sv.id_servicio
        WHERE s.id_cliente = %s
        ORDER BY s.id_solicitud DESC
    """, (id_cliente,))


# ---------------------------------------------------------------
# Solicitudes: SELECT / INSERT / UPDATE / DELETE
# ---------------------------------------------------------------
def listar_solicitudes(busqueda=""):
    """SELECT con JOIN de 3 tablas (solicitudes, clientes, servicios) y WHERE opcional."""
    sql = """
        SELECT s.id_solicitud, c.nombre AS cliente, s.descripcion, sv.nombre AS tipo
        FROM solicitudes s
        INNER JOIN clientes c ON s.id_cliente = c.id_cliente
        INNER JOIN servicios sv ON s.id_servicio = sv.id_servicio
    """
    params = ()
    if busqueda:
        sql += " WHERE c.nombre ILIKE %s OR s.descripcion ILIKE %s"
        patron = f"%{busqueda}%"
        params = (patron, patron)
    sql += " ORDER BY s.id_solicitud DESC"
    return consultar(sql, params)


def obtener_solicitud(id_solicitud):
    return consultar(
        "SELECT id_solicitud, id_cliente, id_servicio, descripcion "
        "FROM solicitudes WHERE id_solicitud = %s",
        (id_solicitud,), uno=True)


def crear_solicitud(id_cliente, id_servicio, descripcion):
    ejecutar(
        "INSERT INTO solicitudes (id_cliente, id_servicio, descripcion) "
        "VALUES (%s, %s, %s)",
        (id_cliente, id_servicio, descripcion))


def actualizar_solicitud(id_solicitud, id_cliente, id_servicio, descripcion):
    ejecutar(
        "UPDATE solicitudes SET id_cliente = %s, id_servicio = %s, descripcion = %s "
        "WHERE id_solicitud = %s",
        (id_cliente, id_servicio, descripcion, id_solicitud))


def eliminar_solicitud(id_solicitud):
    return ejecutar(
        "DELETE FROM solicitudes WHERE id_solicitud = %s", (id_solicitud,))


# ---------------------------------------------------------------
# Resúmenes para el panel
# ---------------------------------------------------------------
def resumen_por_servicio():
    """Cuenta solicitudes por servicio (JOIN + GROUP BY)."""
    return consultar("""
        SELECT sv.nombre AS tipo, COUNT(s.id_solicitud) AS total
        FROM servicios sv
        LEFT JOIN solicitudes s ON s.id_servicio = sv.id_servicio
        GROUP BY sv.id_servicio, sv.nombre
        ORDER BY sv.id_servicio
    """)


def total_clientes():
    return consultar("SELECT COUNT(*) AS total FROM clientes", uno=True)["total"]


# ---------------------------------------------------------------
# Pagos por transferencia
# ---------------------------------------------------------------
_SELECT_PAGO = """
    SELECT p.id_pago, p.id_usuario, p.monto, p.codigo_transferencia, p.estado,
           p.fecha, u.usuario, sv.nombre AS servicio
    FROM pagos p
    INNER JOIN usuarios u ON p.id_usuario = u.id
    INNER JOIN servicios sv ON p.id_servicio = sv.id_servicio
"""


def crear_pago(id_usuario, id_servicio, monto, codigo, imagen, tipo_imagen):
    """INSERT del pago; devuelve el id_pago nuevo (RETURNING)."""
    return ejecutar(
        "INSERT INTO pagos (id_usuario, id_servicio, monto, codigo_transferencia, "
        "comprobante, comprobante_tipo) VALUES (%s, %s, %s, %s, %s, %s) "
        "RETURNING id_pago",
        (id_usuario, id_servicio, monto, codigo, psycopg2.Binary(imagen), tipo_imagen),
        retornar=True)


def listar_pagos(id_usuario=None):
    """SELECT con JOIN (pagos, usuarios, servicios); WHERE si es de un usuario."""
    sql, params = _SELECT_PAGO, ()
    if id_usuario is not None:
        sql += " WHERE p.id_usuario = %s"
        params = (id_usuario,)
    sql += " ORDER BY p.id_pago DESC"
    return consultar(sql, params)


def obtener_pago(id_pago):
    return consultar(_SELECT_PAGO + " WHERE p.id_pago = %s", (id_pago,), uno=True)


def obtener_comprobante(id_pago):
    return consultar(
        "SELECT id_usuario, comprobante, comprobante_tipo FROM pagos WHERE id_pago = %s",
        (id_pago,), uno=True)


def actualizar_estado_pago(id_pago, estado):
    return ejecutar("UPDATE pagos SET estado = %s WHERE id_pago = %s",
                    (estado, id_pago))


def total_pagos_pendientes():
    return consultar("SELECT COUNT(*) AS total FROM pagos WHERE estado = 'pendiente'",
                     uno=True)["total"]
