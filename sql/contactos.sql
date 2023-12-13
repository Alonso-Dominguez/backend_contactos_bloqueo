-- Crear la tabla de contactos
CREATE TABLE IF NOT EXISTS contactos (
    id_contacto INTEGER PRIMARY KEY,
    nombre TEXT,
    primer_apellido TEXT,
    segundo_apellido TEXT,
    email TEXT,
    telefono TEXT
);

-- Base de Datos para Contactos y usuarios --

DROP TABLE IF EXISTS usuarios;

-- Tabla que almacenará los contactos
CREATE TABLE IF NOT EXISTS  usuarios(
    username varchar(50) NOT NULL PRIMARY KEY,
    password varchar(121) NOT NULL,
    token varchar(121) NOT NULL DEFAULT NULL,
    timestamps TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--Contra: 123456                                                         
INSERT INTO usuarios (username, password, token) VALUES ('jose@gmail.com', 'e10adc3949ba59abbe56e057f20f883e', '');

--Contra: 654321
INSERT INTO usuarios (username, password, token) VALUES ('alfredo@gmail.com', 'C33367701511B4F6020EC61DED352059', '');
