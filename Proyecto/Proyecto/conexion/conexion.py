"""Conexión centralizada a PostgreSQL.

- En Render se usa la variable DATABASE_URL (la entrega la base de datos de Render).
- En tu computador se usan DB_HOST, DB_PORT, DB_USER, DB_PASSWORD y DB_NAME
  del archivo .env (que NO se sube a GitHub).
"""
import os

import psycopg2
from psycopg2.extras import RealDictCursor

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:  # python-dotenv es opcional
    pass

RUTA_ESQUEMA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "sql", "esquema.sql")


def get_connection():
    """Abre y devuelve una nueva conexión a PostgreSQL."""
    url = os.environ.get("DATABASE_URL")
    if url:
        return psycopg2.connect(url)
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", 5432)),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", ""),
        dbname=os.environ.get("DB_NAME", "leggy"),
    )


def probar_conexion():
    """Devuelve True si Flask logra conectarse a la base de datos."""
    try:
        conn = get_connection()
        conn.close()
        return True
    except psycopg2.Error as error:
        print(f"[ERROR] No se pudo conectar a PostgreSQL: {error}")
        return False


def consultar(sql, params=(), uno=False):
    """Ejecuta un SELECT parametrizado. Devuelve fetchall() o fetchone().

    Los registros llegan como diccionarios (columna -> valor).
    """
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(sql, params)
        return cursor.fetchone() if uno else cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def ejecutar(sql, params=(), retornar=False):
    """Ejecuta INSERT / UPDATE / DELETE parametrizado con commit().

    Devuelve las filas afectadas (o, con retornar=True, el primer valor de
    RETURNING, por ejemplo el id nuevo). Hace rollback si algo falla.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(sql, params)
        valor = cursor.fetchone()[0] if retornar else cursor.rowcount
        conn.commit()
        return valor
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def inicializar_bd():
    """Ejecuta sql/esquema.sql (crea las tablas si no existen). Es repetible."""
    with open(RUTA_ESQUEMA, encoding="utf-8") as archivo:
        script = archivo.read()
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(script)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
