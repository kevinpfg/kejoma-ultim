-- =========================================================
--  BASE DE DATOS COMPLETA DE LA TIENDA KEJOMA
--  Generada a partir de TODOS los productos de tu index.html
--  Pega este script completo en phpMyAdmin > pestaña SQL
-- =========================================================

CREATE DATABASE IF NOT EXISTS kejoma_db;
USE kejoma_db;

-- Administrador único (tú). La contraseña se crea aparte con crear_admin.py
CREATE TABLE administradores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categorias (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre_categoria VARCHAR(50) NOT NULL,
    slug VARCHAR(50) NOT NULL UNIQUE
);

INSERT INTO categorias (nombre_categoria, slug) VALUES
('Zapatos', 'zapatos'),
('Uniformes', 'uniformes'),
('Balones', 'balones'),
('Porteros', 'porteros'),
('Medias', 'medias');

CREATE TABLE productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    marca VARCHAR(50) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    precio_original DECIMAL(10,2) DEFAULT NULL,
    descuento INT DEFAULT 0,
    stock INT NOT NULL DEFAULT 20,
    estado ENUM('Activo','Inactivo') DEFAULT 'Activo',
    id_categoria INT NOT NULL,
    imagen VARCHAR(255),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria)
);

CREATE TABLE ventas (
    id_venta INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

-- 104 productos extraídos directamente de tu index.html
INSERT INTO productos (nombre, marca, precio, precio_original, descuento, id_categoria, imagen) VALUES
('MAX SPORT Pro', 'Max Sport', 105000, 150000, 30, 1, 'img max 1.webp'),
('MAX SPORT Speed', 'Max Sport', 160000, NULL, 0, 1, 'img max 2.webp'),
('MAX SPORT Run', 'Max Sport', 155000, NULL, 0, 1, 'img max 3.jpg'),
('MAX SPORT Elite', 'Max Sport', 165000, NULL, 0, 1, 'img max 4.webp'),
('MAX SPORT Chart', 'Max Sport', 165000, NULL, 0, 1, 'img max 5.webp'),
('MAX SPORT Running', 'Max Sport', 155000, NULL, 0, 1, 'img max 6.webp'),
('MAX SPORT Retro', 'Max Sport', 165000, NULL, 0, 1, 'img max 7.webp'),
('MAX SPORT Retro Elite', 'Max Sport', 165000, NULL, 0, 1, 'img max 8.webp'),
('Nike Air', 'Nike', 135000, 180000, 25, 1, 'img nike 1.jpg'),
('Nike Zoom', 'Nike', 190000, NULL, 0, 1, 'img nike 2.jpg'),
('Nike Run', 'Nike', 185000, NULL, 0, 1, 'img nike 3.jpg'),
('Nike Pro', 'Nike', 200000, NULL, 0, 1, 'img nike 4.jpg'),
('Nike Pro X', 'Nike', 200000, NULL, 0, 1, 'img nike 5.webp'),
('Nike Run X', 'Nike', 185000, NULL, 0, 1, 'img nike 6.webp'),
('Nike Elite', 'Nike', 200000, NULL, 0, 1, 'img nike 7.webp'),
('Nike Ultra', 'Nike', 200000, NULL, 0, 1, 'img nike 8.webp'),
('JOMA Classic', 'Joma', 220000, NULL, 0, 1, 'img joma 1.webp'),
('JOMA Speed', 'Joma', 210000, NULL, 0, 1, 'img joma 2.webp'),
('JOMA TREDRI', 'Joma', 195000, NULL, 0, 1, 'img joma 3.jpg'),
('JOMA ASTRAL', 'Joma', 205000, NULL, 0, 1, 'img joma 4.webp'),
('JOMA Elite Roca', 'Joma', 205000, NULL, 0, 1, 'img joma 5.jpg'),
('JOMA Runner', 'Joma', 195000, NULL, 0, 1, 'img joma 6.jpg'),
('JOMA Elite Pro', 'Joma', 205000, NULL, 0, 1, 'img joma 7.webp'),
('JOMA Elite', 'Joma', 205000, NULL, 0, 1, 'img joma 8.jpeg'),
('Adidas Rpro', 'Adidas', 170900, NULL, 0, 1, 'img adidas 1.jpg'),
('Adidas Run', 'Adidas', 180000, NULL, 0, 1, 'img adidas 2.webp'),
('Adidas Saurio', 'Adidas', 170000, NULL, 0, 1, 'img adidas 3.jpg'),
('Adidas Glass', 'Adidas', 175000, NULL, 0, 1, 'img adidas 4.jpg'),
('Adidas Classic', 'Adidas', 175000, NULL, 0, 1, 'img adidas 5.webp'),
('Adidas Sport', 'Adidas', 170000, NULL, 0, 1, 'img adidas 6.jpg'),
('Adidas Air', 'Adidas', 175000, NULL, 0, 1, 'img adidas 7.jfif'),
('Adidas Boost', 'Adidas', 175000, NULL, 0, 1, 'img adidas 8.jpg'),
('KEJOMA JR Pro', 'Kejoma', 170900, NULL, 0, 1, 'img kejoma 1.png'),
('KEJOMA JR Fulty', 'Kejoma', 180000, NULL, 0, 1, 'img kejoma 2.png'),
('KEJOMA JR Good', 'Kejoma', 140000, NULL, 0, 1, 'img kejoma 3.png'),
('KEJOMA JR Freestyler', 'Kejoma', 160000, NULL, 0, 1, 'img kejoma 4.png'),
('KEJOMA JR MKJ', 'Kejoma', 175000, NULL, 0, 1, 'img kejoma 5.png'),
('KEJOMA JR Good Pro', 'Kejoma', 170000, NULL, 0, 1, 'img kejoma 6.png'),
('KEJOMA JR Repro', 'Kejoma', 178000, NULL, 0, 1, 'img kejoma 7.png'),
('KEJOMA JR Mate', 'Kejoma', 150000, NULL, 0, 1, 'img kejoma 8.png'),
('MAX SPORT Uniforme 1', 'Max Sport', 110000, NULL, 0, 2, 'MAX SPORT Uniforme 1 a.png'),
('MAX SPORT Uniforme 2', 'Max Sport', 115000, NULL, 0, 2, 'MAX SPORT Uniforme 2 a.png'),
('MAX SPORT Uniforme 3', 'Max Sport', 120000, NULL, 0, 2, 'MAX SPORT Uniforme 3 a.png'),
('MAX SPORT Uniforme 4', 'Max Sport', 125000, NULL, 0, 2, 'MAX SPORT Uniforme 4 a.png'),
('MAX SPORT Uniforme 5', 'Max Sport', 130000, NULL, 0, 2, 'MAX SPORT Uniforme 5 a.png'),
('MAX SPORT Uniforme 6', 'Max Sport', 135000, NULL, 0, 2, 'MAX SPORT Uniforme 6 a.png'),
('MAX SPORT Uniforme 7', 'Max Sport', 140000, NULL, 0, 2, 'MAX SPORT Uniforme 7 a.png'),
('MAX SPORT Uniforme 8', 'Max Sport', 145000, NULL, 0, 2, 'MAX SPORT Uniforme 8 a.png'),
('Nike Dri-FIT Pro', 'Nike', 150000, NULL, 0, 2, 'Nike Dri-FIT Pro 1.png'),
('Nike Strike Elite', 'Nike', 160000, NULL, 0, 2, 'Nike Strike Elite 1.png'),
('Nike Academy', 'Nike', 140000, NULL, 0, 2, 'Nike Academy 1.png'),
('Nike Park 20', 'Nike', 130000, NULL, 0, 2, 'Nike Park 20 1.png'),
('Nike Dri-FIT', 'Nike', 150000, NULL, 0, 2, 'Nike Dri-FIT 1.png'),
('Nike Strike', 'Nike', 160000, NULL, 0, 2, 'Nike Strike 1.png'),
('Nike Air', 'Nike', 140000, NULL, 0, 2, 'Nike Air 1.png'),
('Nike Park 30', 'Nike', 130000, NULL, 0, 2, 'Nike Park 30 1.png'),
('Joma Championship', 'Joma', 125000, NULL, 0, 2, 'jomas 1a.PNG'),
('Joma Winner', 'Joma', 130000, NULL, 0, 2, 'jomas 2a.PNG'),
('Joma Eco-Championship', 'Joma', 135000, NULL, 0, 2, 'jomas 3a.PNG'),
('Joma Tiger', 'Joma', 120000, NULL, 0, 2, 'jomas 4a.PNG'),
('Joma Championship', 'Joma', 125000, NULL, 0, 2, 'jomas 5a.PNG'),
('Joma Winner', 'Joma', 130000, NULL, 0, 2, 'jomas 6a.PNG'),
('Joma Eco-Championship', 'Joma', 135000, NULL, 0, 2, 'jomas 7a.PNG'),
('Joma Tiger', 'Joma', 120000, NULL, 0, 2, 'jomas 8a.PNG'),
('Adidas Tiro 23', 'Adidas', 155000, NULL, 0, 2, 'adidas 1f.png'),
('Adidas Squadra 21', 'Adidas', 145000, NULL, 0, 2, 'adidas 1g.png'),
('Adidas Entrada 22', 'Adidas', 140000, NULL, 0, 2, 'adidas 1h.png'),
('Adidas Condivo Pro', 'Adidas', 165000, NULL, 0, 2, 'adidas 1e.png'),
('Adidas Tiro 23', 'Adidas', 155000, NULL, 0, 2, 'adidas 1d.png'),
('Adidas Squadra 21', 'Adidas', 145000, NULL, 0, 2, 'adidas 1c.png'),
('Adidas Entrada 22', 'Adidas', 140000, NULL, 0, 2, 'adidas 1b.png'),
('Adidas Condivo Pro', 'Adidas', 165000, NULL, 0, 2, 'adidas 1a.png'),
('Kejoma JR Pro Team', 'Kejoma', 115000, NULL, 0, 2, 'kejoma 1a.png'),
('Kejoma JR Classic', 'Kejoma', 105000, NULL, 0, 2, 'kejoma 1b.png'),
('Kejoma JR Elite', 'Kejoma', 120000, NULL, 0, 2, 'kejoma 1c.png'),
('Kejoma JR Flash', 'Kejoma', 110000, NULL, 0, 2, 'kejoma 1d.png'),
('Kejoma JR Pro Team', 'Kejoma', 115000, NULL, 0, 2, 'kejoma 1e.png'),
('Kejoma JR Classic', 'Kejoma', 105000, NULL, 0, 2, 'kejoma 1f.png'),
('Kejoma JR Elite', 'Kejoma', 120000, NULL, 0, 2, 'kejoma 1g.png'),
('Kejoma JR Flash', 'Kejoma', 110000, NULL, 0, 2, 'kejoma 1h.png'),
('Balón MAX SPORT Pro', 'Max Sport', 85000, NULL, 0, 3, 'balon 1a.PNG'),
('Balón Nike Flight', 'Nike', 96000, 120000, 20, 3, 'balon 2b.PNG'),
('Balón Adidas UCL', 'Adidas', 130000, NULL, 0, 3, 'balon 3b.PNG'),
('Balón JOMA Dali III', 'Joma', 75000, NULL, 0, 3, 'balon 4b.PNG'),
('Balón KEJOMA Street', 'Kejoma', 65000, NULL, 0, 3, 'balon 5b.PNG'),
('Balón Nike Strike', 'Nike', 95000, NULL, 0, 3, 'balon 6b.PNG'),
('Balón Adidas Tiro', 'Adidas', 70000, NULL, 0, 3, 'balon 7b.PNG'),
('Balón MAX SPORT Training', 'Max Sport', 60000, NULL, 0, 3, 'balon 8b.PNG'),
('Guantes Portero Pro', 'Kejoma', 61750, 95000, 35, 4, 'portero 1a.PNG'),
('Camiseta Portero Acolchada', 'Kejoma', 120000, NULL, 0, 4, 'portero 2a.PNG'),
('Pantalón Portero con Rodilleras', 'Kejoma', 110000, NULL, 0, 4, 'portero 3a.jpg'),
('Kit Portero Adidas Predator', 'Adidas', 280000, NULL, 0, 4, 'portero 4a.PNG'),
('Guantes Nike Match', 'Nike', 85000, NULL, 0, 4, 'portero 5a.PNG'),
('Guantes Joma Superset', 'Joma', 78000, NULL, 0, 4, 'portero 6a.PNG'),
('Guantes Joma Superset', 'Joma', 78000, NULL, 0, 4, 'portero 7a.PNG'),
('Guantes Joma Superset', 'Joma', 78000, NULL, 0, 4, 'portero 8a.PNG'),
('Medias KEJOMA Pro', 'Kejoma', 18000, NULL, 0, 5, 'imgmedia1a.png'),
('Medias Nike Strike', 'Nike', 32000, NULL, 0, 5, 'imgmedia2a.png'),
('Medias Adidas Milano', 'Adidas', 28000, NULL, 0, 5, 'imgmedia3a.png'),
('Medias Joma Calcio', 'Joma', 22000, NULL, 0, 5, 'imgmedia4a.png'),
('Medias MAX SPORT Elite', 'Max Sport', 20000, NULL, 0, 5, 'imgmedia5a.png'),
('Medias Portero Acolchadas', 'Kejoma', 25000, NULL, 0, 5, 'imgmedia6a.png'),
('Medias Portero Acolchadas', 'Kejoma', 25000, NULL, 0, 5, 'imgmedia7a.png'),
('Medias Portero Acolchadas', 'Kejoma', 25000, NULL, 0, 5, 'imgmedia8a.png');
