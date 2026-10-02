"""Crea las tablas en PostgreSQL ejecutando sql/esquema.sql.

Uso:  python init_db.py
"""
from conexion import inicializar_bd

inicializar_bd()
print("Tablas creadas / verificadas correctamente.")
