# 💳 Totalnet BI — Inteligencia Comercial & Salud Operativa de Adquirencia (Uruguay)

Proyecto *end-to-end* de Business Intelligence y Data Analytics simulando la operación multi-adquirente de **Totalnet** en Uruguay, abarcando generación sintética de datos, ETL en PostgreSQL con deduplicación transaccional y visualización ejecutiva en Power BI[cite: 17].

---

## 🏗️ Arquitectura del Pipeline

1. **Generación de Datos (`generate_data.py`):** Simulación de 250 comercios uruguayos (`dim_comercios.csv`) y 18.015 intentos transaccionales (`fact_transacciones.csv`), modelando estacionalidad de cobro de sueldos, estructura de aranceles por rubro/canal, reintentos duplicados de POS y una anomalía técnica regional[cite: 13, 17].
2. **Data Warehousing & ETL (`PostgreSQL`):**
   - Ingesta masiva mediante `COPY` hacia tabla de *staging* (`stg_transacciones`).
   - Auditoría y deduplicación mediante *Window Functions* (`ROW_NUMBER() OVER(PARTITION BY transaction_id)`), eliminando 15 reintentos duplicados de POS antes de la liquidación.
   - Modelado en **Esquema Estrella** (`dim_comercios` + `fact_transacciones`) con integridad referencial (`PK`/`FK`) y cálculo financiero de arancel y neto a liquidar[cite: 17].
   - Creación de vistas analíticas para consumo ejecutivo (`vw_resumen_ejecutivo_comercios` y `vw_monitoreo_anomalias_red`).
3. **Modelado Semántico & Visualización (`Power BI` + `DAX`):**
   - Tabla dedicada de 9 medidas DAX: *TPV Aprobado (UYU)*, *Ingresos Arancel (UYU)*, *Neto Liquidado Comercios (UYU)*, *Take Rate Efectivo %*, *Ticket Promedio (UYU)*, *Total Intentos*, *Tx Aprobadas*, *Tasa Aprobación %* y *Tasa Falla Técnica %*[cite: 13, 16].

---

## 💡 Principales Hallazgos de Negocio

* **Volumen y Rentabilidad:** Se procesaron **$30,70M UYU** en TPV aprobado (16.499 transacciones aprobadas sobre 18.000 intentos únicos), logrando una tasa de aprobación global del **91,66 %**, un ticket promedio de **$1,86K UYU** y **$641,66K UYU** en ingresos por aranceles (*Take Rate efectivo* del **2,09 %**)[cite: 13, 16].
* **Diagnóstico de Rechazos (Comercial vs. Técnico):** Del total de operaciones rechazadas, el **62,29 %** responde a *Fondos Insuficientes*, pero un **37,71 %** corresponde a fallas técnicas recuperables (**25,05 %** *Error Red/POS* y **12,66 %** *Timeout*), representando una oportunidad directa de recupero de TPV[cite: 13].
* **Anomalía Regional Detectada:** El monitoreo cruzado por departamento y canal identificó una degradación en la estabilidad de terminales **Smart POS en Canelones** (tasa de falla técnica del **4,04 %** sobre alto volumen transaccional), permitiendo focalizar acciones preventivas de soporte técnico y conectividad[cite: 13].

---

## 📊 Vistas del Dashboard (Power BI)

### 1. Resumen Ejecutivo & Liquidación Comercial
![Resumen Ejecutivo](Resumen%20Ejecutivo.png)[cite: 16, 17]

### 2. Salud Operativa & Auditoría de Red
![Salud Operativa](Salud%20operativa%20y%20rechazos.png)[cite: 13, 17]

---

## 📂 Estructura del Repositorio

* `generate_data.py` — Script en Python para generación reproducible de comercios, transacciones y anomalías operativas[cite: 17].
* `dim_comercios.csv` — Tabla maestra de comercios (rubro, departamento, tamaño y canal principal)[cite: 17].
* `fact_transacciones.csv` — Tabla de hechos transaccionales[cite: 17].
* `TotalNet/` — Scripts SQL del pipeline ETL (`totalnet_etl.sql`) y archivo fuente de Power BI (`TotalNet_BI_Dashboard.pbix`)[cite: 17].
* `Resumen Ejecutivo.png` & `Salud operativa y rechazos.png` — Capturas ejecutivas del dashboard final[cite: 17].
