# 💳 Totalnet BI — Inteligencia Comercial & Salud Operativa de Adquirencia

Análisis estratégico del ecosistema multi-adquirente de pagos electrónicos en Uruguay orientado a monitorear el volumen procesado (TPV), la rentabilidad por aranceles, la liquidación neta a comercios y la estabilidad técnica de la red mediante ingeniería de datos en PostgreSQL y visualización ejecutiva en Power BI[cite: 11, 12].

---

# 🎯 Objetivo del Proyecto

Desarrollar un sistema integral de inteligencia de negocio y monitoreo operativo que permita auditar y optimizar:

- Volumen total procesado (TPV) y estacionalidad de consumo[cite: 11]
- Rentabilidad por aranceles (*Take Rate* efectivo) y liquidación neta a comercios[cite: 11]
- Tasa de aprobación transaccional y causas de rechazo[cite: 8, 11]
- Estabilidad técnica por canal de captura y departamento geográfico[cite: 8]

El proyecto busca transformar registros transaccionales crudos en indicadores accionables para maximizar la tasa de aprobación y anticipar degradaciones operativas en terminales de pago[cite: 8, 11].

---

# 🧠 Problema de Negocio

En operaciones de adquirencia multi-canal, la falta de visibilidad consolidada entre el desempeño financiero y la salud técnica de la red genera:

- Pérdida directa de volumen transaccional (TPV) por rechazos técnicos evitables (*timeouts* y errores de red/POS)[cite: 8]
- Dificultad para distinguir rechazos comerciales del emisor frente a fallas operativas propias de la infraestructura[cite: 8]
- Riesgo de liquidación duplicada ante reintentos automáticos de terminales POS
- Falta de detección temprana sobre degradaciones regionales en canales específicos[cite: 8]

👉 Pregunta central del análisis:

**¿Qué factores comerciales y técnicos están impactando la conversión transaccional y la rentabilidad de la red, y dónde focalizar acciones preventivas para recuperar TPV?**

---

# 🚀 Resultados Clave del Negocio

| KPI Estratégico | Resultado |
|---|---|
| Volumen procesado (TPV Aprobado) | $30.697.991,39 UYU ($30,70 mill.) sobre 16.499 transacciones aprobadas[cite: 8, 11] |
| Rentabilidad por aranceles | $641,66 mil UYU generados con un *Take Rate* efectivo del 2,09%[cite: 11] |
| Conversión global de red | 91,66% de tasa de aprobación sobre 18.000 intentos únicos validados[cite: 8] |
| Composición de rechazos | 62,29% por fondos insuficientes vs. 37,71% por fallas técnicas (25,05% Error Red/POS y 12,66% Timeout)[cite: 8] |
| Anomalía regional detectada | Tasa de falla técnica del 4,04% en terminales Smart POS en Canelones sobre alto volumen operativo[cite: 8] |

---

# 💡 Recomendaciones Estratégicas

| Oportunidad Detectada | Impacto Potencial |
|---|---|
| Auditoría técnica y actualización de firmware en Smart POS de Canelones[cite: 8] | Reducción de fallas técnicas regionales por debajo del umbral operativo del 2,5% |
| Optimización de *timeouts* y enrutamiento en franjas pico (10:00 a 21:00 hs)[cite: 8] | Recupero directo de hasta un 15% a 20% de las transacciones rechazadas por motivos técnicos[cite: 8] |
| Fidelización comercial en rubros líderes (Supermercados, Indumentaria y Gastronomía)[cite: 11] | Protección del 63% del TPV aprobado y estabilidad en el ingreso por aranceles[cite: 11] |
| Reglas automatizadas de deduplicación en etapa de *staging* ETL | Eliminación del 100% de riesgo por doble liquidación ante reintentos de POS |

---

# 📊 Dashboard Ejecutivo

### 1. Resumen Ejecutivo & Liquidación Comercial
![Resumen Ejecutivo](Resumen%20Ejecutivo.png)[cite: 11, 12]

### 2. Salud Operativa & Auditoría de Red
![Salud Operativa](Salud%20operativa%20y%20rechazos.png)[cite: 8, 12]

🔗 **Acceso al dashboard interactivo:**  
👉 [Totalnet BI Dashboard (.pbix)](https://github.com/GuilleBerrutti/totalnet-bi-acquiring-analytics/tree/main/TotalNet)[cite: 12]

---

# 📂 Dataset y Arquitectura Utilizada

El pipeline fue desarrollado de extremo a extremo combinando generación sintética reproducible, modelado dimensional en PostgreSQL y explotación semántica en Power BI[cite: 12]:

- **Tabla de Hechos (`fact_transacciones.csv`):** 18.015 registros transaccionales con monto en UYU, canal, sello, cuotas, estado, arancel y neto a liquidar[cite: 12]
- **Tabla Dimensional (`dim_comercios.csv`):** 250 comercios categorizados por rubro, departamento, tamaño y canal principal[cite: 12]
- **ETL & Data Warehouse (`PostgreSQL`):** Deduplicación mediante *Window Functions* (`ROW_NUMBER()`), esquema estrella (`PK`/`FK`) y vistas analíticas
- **Modelado Semántico (`DAX`):** 9 medidas financieras y operativas dedicadas

📥 **Acceso al dataset y código fuente:**  
👉 [Script generador en Python (`generate_data.py`)](https://github.com/GuilleBerrutti/totalnet-bi-acquiring-analytics/blob/main/generate_data.py)[cite: 12]  
👉 [Base transaccional (`fact_transacciones.csv`)](https://github.com/GuilleBerrutti/totalnet-bi-acquiring-analytics/blob/main/fact_transacciones.csv)[cite: 12]  
👉 [Maestro de comercios (`dim_comercios.csv`)](https://github.com/GuilleBerrutti/totalnet-bi-acquiring-analytics/blob/main/dim_comercios.csv)[cite: 12]
