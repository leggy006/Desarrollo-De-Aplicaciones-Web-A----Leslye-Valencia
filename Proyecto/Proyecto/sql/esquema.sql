-- =====================================================
-- Leggy - Esquema PostgreSQL
-- Primero crea la base de datos (una sola vez), por ejemplo en pgAdmin:
--     CREATE DATABASE leggy;
-- Luego ejecuta este archivo:  python init_db.py
-- =====================================================

-- Usuarios que pueden ingresar al sistema (login)
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL          -- hash, nunca texto plano
);

-- Clientes que encargan trabajos
CREATE TABLE IF NOT EXISTS clientes (
    id_cliente SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    correo VARCHAR(100)
);

-- Catálogo de servicios
CREATE TABLE IF NOT EXISTS servicios (
    id_servicio SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL
);

-- Solicitudes: relaciona un cliente con un servicio (2 claves foráneas)
CREATE TABLE IF NOT EXISTS solicitudes (
    id_solicitud SERIAL PRIMARY KEY,
    id_cliente INTEGER NOT NULL,
    id_servicio INTEGER NOT NULL,
    descripcion TEXT NOT NULL,
    CONSTRAINT fk_solicitud_cliente
        FOREIGN KEY (id_cliente) REFERENCES clientes (id_cliente)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_solicitud_servicio
        FOREIGN KEY (id_servicio) REFERENCES servicios (id_servicio)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

INSERT INTO servicios (nombre) VALUES
    ('Retrato personalizado'),
    ('Caricatura a lápiz'),
    ('Pintura personalizada')
ON CONFLICT (nombre) DO NOTHING;

-- Precio fijo de cada servicio (USD). Los valores iniciales solo se aplican
-- mientras el precio sea 0, así no se pisan los cambios que hagas después.
ALTER TABLE servicios ADD COLUMN IF NOT EXISTS precio NUMERIC(10,2) NOT NULL DEFAULT 0;
UPDATE servicios SET precio = 15.00 WHERE nombre = 'Retrato personalizado' AND precio = 0;
UPDATE servicios SET precio = 10.00 WHERE nombre = 'Caricatura a lápiz' AND precio = 0;
UPDATE servicios SET precio = 25.00 WHERE nombre = 'Pintura personalizada' AND precio = 0;

-- Pagos por transferencia (Banco Pichincha): usuario + servicio + comprobante
CREATE TABLE IF NOT EXISTS pagos (
    id_pago SERIAL PRIMARY KEY,
    id_usuario INTEGER NOT NULL,
    id_servicio INTEGER NOT NULL,
    monto NUMERIC(10,2) NOT NULL CHECK (monto > 0),
    codigo_transferencia VARCHAR(50) NOT NULL,
    comprobante BYTEA NOT NULL,                 -- foto del comprobante
    comprobante_tipo VARCHAR(20) NOT NULL,      -- image/jpeg, image/png, image/webp
    estado VARCHAR(15) NOT NULL DEFAULT 'pendiente'
        CHECK (estado IN ('pendiente', 'verificado', 'rechazado')),
    fecha TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'America/Guayaquil'),
    CONSTRAINT fk_pago_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuarios (id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_pago_servicio
        FOREIGN KEY (id_servicio) REFERENCES servicios (id_servicio)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

-- Un mismo código de transferencia no puede usarse dos veces (salvo si fue rechazado)
CREATE UNIQUE INDEX IF NOT EXISTS ux_pagos_codigo
    ON pagos (codigo_transferencia) WHERE estado <> 'rechazado';
