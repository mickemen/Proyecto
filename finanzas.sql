-- 1) Base y tablas
CREATE DATABASE IF NOT EXISTS finanzas CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE finanzas;

CREATE TABLE cuentas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL,
  moneda CHAR(3) NOT NULL DEFAULT 'CRC'
);

CREATE TABLE categorias (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL,
  tipo ENUM('ingreso','gasto') NOT NULL
);

CREATE TABLE transacciones (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  cuenta_id INT NOT NULL,
  categoria_id INT NOT NULL,
  fecha DATE NOT NULL,
  descripcion VARCHAR(200),
  monto DECIMAL(12,2) NOT NULL,  -- positivo para ingresos, negativo para gastos
  CONSTRAINT fk_t_cuenta FOREIGN KEY (cuenta_id) REFERENCES cuentas(id),
  CONSTRAINT fk_t_categoria FOREIGN KEY (categoria_id) REFERENCES categorias(id),
  INDEX idx_fecha (fecha),
  INDEX idx_categoria (categoria_id)
);

CREATE TABLE presupuestos_mensuales (
  id INT AUTO_INCREMENT PRIMARY KEY,
  anio SMALLINT NOT NULL,
  mes TINYINT NOT NULL CHECK (mes BETWEEN 1 AND 12),
  categoria_id INT NOT NULL,
  monto DECIMAL(12,2) NOT NULL,
  UNIQUE KEY uk_presu (anio, mes, categoria_id),
  CONSTRAINT fk_p_categoria FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);

-- 2) Datos de ejemplo
INSERT INTO cuentas (nombre, moneda) VALUES ('Cuenta Banco', 'CRC'), ('Efectivo', 'CRC');

INSERT INTO categorias (nombre, tipo) VALUES
('Salario','ingreso'),
('Ventas','ingreso'),
('Supermercado','gasto'),
('Transporte','gasto'),
('Servicios públicos','gasto');

INSERT INTO presupuestos_mensuales (anio, mes, categoria_id, monto) VALUES
(2025,10, (SELECT id FROM categorias WHERE nombre='Supermercado'), 150000),
(2025,10, (SELECT id FROM categorias WHERE nombre='Transporte'),   40000),
(2025,10, (SELECT id FROM categorias WHERE nombre='Servicios públicos'), 90000);

INSERT INTO transacciones (cuenta_id, categoria_id, fecha, descripcion, monto) VALUES
(1, (SELECT id FROM categorias WHERE nombre='Salario'), '2025-10-01', 'Pago mensual', 1500000.00),
(1, (SELECT id FROM categorias WHERE nombre='Supermercado'), '2025-10-05', 'Compras semana 1', -52000.00),
(1, (SELECT id FROM categorias WHERE nombre='Transporte'), '2025-10-06', 'Buses y Uber', -8500.00),
(2, (SELECT id FROM categorias WHERE nombre='Supermercado'), '2025-10-12', 'Verduras', -21000.00),
(1, (SELECT id FROM categorias WHERE nombre='Servicios públicos'), '2025-10-15', 'Luz + Agua', -73500.00),
(1, (SELECT id FROM categorias WHERE nombre='Ventas'), '2025-10-18', 'Venta freelance', 200000.00);

-- 3) Vistas útiles
CREATE OR REPLACE VIEW v_resumen_mensual AS
SELECT
  DATE_FORMAT(fecha, '%Y-%m') AS anio_mes,
  SUM(CASE WHEN c.tipo='ingreso' THEN monto ELSE 0 END) AS ingresos,
  SUM(CASE WHEN c.tipo='gasto'   THEN -monto ELSE 0 END) AS gastos,   -- convertimos a positivo
  SUM(monto) AS balance
FROM transacciones t
JOIN categorias c ON c.id = t.categoria_id
GROUP BY 1;

CREATE OR REPLACE VIEW v_gasto_por_categoria_mes AS
SELECT
  DATE_FORMAT(t.fecha, '%Y-%m') AS anio_mes,
  c.nombre AS categoria,
  SUM(-t.monto) AS gasto_total
FROM transacciones t
JOIN categorias c ON c.id = t.categoria_id
WHERE c.tipo='gasto'
GROUP BY 1,2;

-- 4) Reportes típicos
-- 4.1 Resumen del mes actual (ajusta '2025-10' si hace falta)
SELECT * FROM v_resumen_mensual WHERE anio_mes='2025-10';

-- 4.2 Top categorías de gasto en el mes
SELECT * FROM v_gasto_por_categoria_mes
WHERE anio_mes='2025-10'
ORDER BY gasto_total DESC;

-- 4.3 Presupuesto vs. gasto real por categoría del mes
SELECT
  p.anio, p.mes, c.nombre AS categoria,
  p.monto AS presupuesto,
  IFNULL(SUM(CASE WHEN t.monto < 0 THEN -t.monto ELSE 0 END),0) AS gasto_real,
  (p.monto - IFNULL(SUM(CASE WHEN t.monto < 0 THEN -t.monto ELSE 0 END),0)) AS diferencia
FROM presupuestos_mensuales p
JOIN categorias c ON c.id = p.categoria_id
LEFT JOIN transacciones t
  ON t.categoria_id = p.categoria_id
  AND YEAR(t.fecha)=p.anio AND MONTH(t.fecha)=p.mes
GROUP BY p.anio, p.mes, c.nombre, p.monto
ORDER BY c.nombre;

-- 5) Trigger opcional: evitar que un ingreso se guarde con monto negativo (o gasto positivo)
DELIMITER //
CREATE TRIGGER tr_montos_signo BEFORE INSERT ON transacciones
FOR EACH ROW
BEGIN
  DECLARE v_tipo ENUM('ingreso','gasto');
  SELECT tipo INTO v_tipo FROM categorias WHERE id = NEW.categoria_id;
  IF v_tipo='ingreso' AND NEW.monto < 0 THEN
    SET NEW.monto = -NEW.monto;
  END IF;
  IF v_tipo='gasto' AND NEW.monto > 0 THEN
    SET NEW.monto = -NEW.monto;
  END IF;
END//
DELIMITER ;
