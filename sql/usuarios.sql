CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    usuario varchar(255) NOT NULL UNIQUE,
    contrasena varchar(255) NOT NULL, 
    token varchar(255) NOT NULL,
    timestamps TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);