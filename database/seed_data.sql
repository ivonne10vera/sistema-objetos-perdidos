CREATE DATABASE IF NOT EXISTS objetos_perdidos_db;
USE objetos_perdidos_db;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    rol ENUM('estudiante', 'administrador') DEFAULT 'estudiante'
);

CREATE TABLE categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

CREATE TABLE objetos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(100) NOT NULL,
    descripcion TEXT NOT NULL,
    tipo_reporte ENUM('extraviado', 'encontrado') NOT NULL,
    fecha DATE NOT NULL,
    lugar VARCHAR(100) NOT NULL,
    estado ENUM('reportado', 'encontrado', 'reclamado', 'entregado') DEFAULT 'reportado',
    id_categoria INT NOT NULL,
    id_usuario INT NOT NULL,
    FOREIGN KEY (id_categoria) REFERENCES categorias(id),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
);

CREATE TABLE solicitudes_reclamo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_objeto INT NOT NULL,
    id_usuario_reclamante INT NOT NULL,
    justificacion TEXT NOT NULL,
    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado_solicitud ENUM('pendiente', 'aprobada', 'rechazada') DEFAULT 'pendiente',
    FOREIGN KEY (id_objeto) REFERENCES objetos(id),
    FOREIGN KEY (id_usuario_reclamante) REFERENCES usuarios(id)
);