DROP TABLE IF EXISTS stg_transacciones CASCADE;
DROP TABLE IF EXISTS dim_comercios CASCADE;

CREATE TABLE dim_comercios (
    merchant_id VARCHAR(20) PRIMARY KEY,
    nombre_comercio VARCHAR(100) NOT NULL,
    rubro VARCHAR(50) NOT NULL,
    departamento VARCHAR(50) NOT NULL,
    tamano_comercio VARCHAR(20) NOT NULL,
    canal_principal VARCHAR(50) NOT NULL,
    fecha_alta DATE NOT NULL
);

CREATE TABLE stg_transacciones (
    transaction_id VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    merchant_id VARCHAR(20) NOT NULL,
    canal VARCHAR(50) NOT NULL,
    sello VARCHAR(30) NOT NULL,
    tipo_tarjeta VARCHAR(20) NOT NULL,
    cuotas INT NOT NULL,
    monto_uyu NUMERIC(12, 2) NOT NULL,
    arancel_pct NUMERIC(6, 4) NOT NULL,
    estado VARCHAR(50) NOT NULL
);

COPY dim_comercios 
FROM 'C:\Users\Asus\Desktop\GitHub\TotalNet\dim_comercios.csv' 
WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

COPY stg_transacciones 
FROM 'C:\Users\Asus\Desktop\GitHub\TotalNet\fact_transacciones.csv' 
WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

-- ============================================================================
-- BLOQUE 2: AUDITORÍA DE DUPLICADOS Y CONSTRUCCIÓN DE FACT_TRANSACCIONES
-- ============================================================================

-- 1. Auditoría: Detectar transacciones duplicadas en staging
SELECT 
    transaction_id, 
    COUNT(*) AS repeticiones,
    SUM(monto_uyu) AS monto_total_bruto
FROM stg_transacciones
GROUP BY transaction_id
HAVING COUNT(*) > 1
ORDER BY repeticiones DESC;

-- 2. Crear tabla limpia de producción con Foreign Key y Primary Key
DROP TABLE IF EXISTS fact_transacciones CASCADE;

CREATE TABLE fact_transacciones AS
WITH transacciones_deduplicadas AS (
    SELECT 
        *,
        ROW_NUMBER() OVER(
            PARTITION BY transaction_id 
            ORDER BY timestamp ASC
        ) AS rn
    FROM stg_transacciones
)
SELECT 
    transaction_id,
    timestamp,
    DATE(timestamp) AS fecha,
    EXTRACT(HOUR FROM timestamp)::INT AS hora,
    merchant_id,
    canal,
    sello,
    tipo_tarjeta,
    cuotas,
    monto_uyu,
    arancel_pct,
    estado,
    -- Lógica financiera de adquirencia (solo se liquida lo 'Aprobada')
    CASE 
        WHEN estado = 'Aprobada' THEN ROUND(monto_uyu * arancel_pct, 2)
        ELSE 0.00 
    END AS ingreso_arancel_uyu,
    CASE 
        WHEN estado = 'Aprobada' THEN ROUND(monto_uyu * (1 - arancel_pct), 2)
        ELSE 0.00 
    END AS neto_liquidar_comercio_uyu
FROM transacciones_deduplicadas
WHERE rn = 1;

-- 3. Agregar integridad referencial y claves primarias
ALTER TABLE fact_transacciones ADD PRIMARY KEY (transaction_id);
ALTER TABLE fact_transacciones ADD CONSTRAINT fk_comercio 
    FOREIGN KEY (merchant_id) REFERENCES dim_comercios(merchant_id);

-- 4. Verificar conteo final limpio (debe dar exactamente 18.000 filas)
SELECT COUNT(*) AS total_transacciones_limpias FROM fact_transacciones;

-- ============================================================================
-- BLOQUE 3: VISTAS ANALÍTICAS PARA POWER BI Y AUDITORÍA DE RED
-- ============================================================================

-- 1. Vista ejecutiva por comercio y segmento (TPV, Aranceles, Tasa de Aprobación)
CREATE OR REPLACE VIEW vw_resumen_ejecutivo_comercios AS
SELECT 
    c.merchant_id,
    c.nombre_comercio,
    c.rubro,
    c.departamento,
    c.tamano_comercio,
    c.canal_principal,
    COUNT(f.transaction_id) AS total_intentos,
    SUM(CASE WHEN f.estado = 'Aprobada' THEN 1 ELSE 0 END) AS tx_aprobadas,
    SUM(CASE WHEN f.estado <> 'Aprobada' THEN 1 ELSE 0 END) AS tx_rechazadas,
    ROUND(
        100.0 * SUM(CASE WHEN f.estado = 'Aprobada' THEN 1 ELSE 0 END) / NULLIF(COUNT(f.transaction_id), 0), 
        2
    ) AS tasa_aprobacion_pct,
    SUM(CASE WHEN f.estado = 'Aprobada' THEN f.monto_uyu ELSE 0 END) AS tpv_aprobado_uyu,
    ROUND(
        AVG(CASE WHEN f.estado = 'Aprobada' THEN f.monto_uyu END), 
        2
    ) AS ticket_promedio_uyu,
    SUM(f.ingreso_arancel_uyu) AS ingreso_arancel_total_uyu,
    SUM(f.neto_liquidar_comercio_uyu) AS neto_liquidado_uyu
FROM dim_comercios c
LEFT JOIN fact_transacciones f ON c.merchant_id = f.merchant_id
GROUP BY 
    c.merchant_id, c.nombre_comercio, c.rubro, 
    c.departamento, c.tamano_comercio, c.canal_principal;

-- 2. Vista de auditoría técnica por departamento y canal (detección de anomalía regional)
CREATE OR REPLACE VIEW vw_monitoreo_anomalias_red AS
SELECT 
    c.departamento,
    f.canal,
    f.estado,
    COUNT(f.transaction_id) AS cantidad_tx,
    SUM(f.monto_uyu) AS volumen_intentado_uyu,
    ROUND(
        100.0 * COUNT(f.transaction_id) / SUM(COUNT(f.transaction_id)) OVER(PARTITION BY c.departamento, f.canal),
        2
    ) AS pct_dentro_depto_canal
FROM fact_transacciones f
JOIN dim_comercios c ON f.merchant_id = c.merchant_id
GROUP BY c.departamento, f.canal, f.estado
ORDER BY c.departamento, f.canal, cantidad_tx DESC;

-- 3. Consulta rápida de validación para verificar los hallazgos de negocio
SELECT * FROM vw_monitoreo_anomalias_red
WHERE departamento IN ('Montevideo', 'Canelones')
ORDER BY departamento, canal, cantidad_tx DESC;