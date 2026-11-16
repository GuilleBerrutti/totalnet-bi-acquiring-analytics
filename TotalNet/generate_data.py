import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Configuración de semilla para reproducibilidad
np.random.seed(42)
random.seed(42)

# Parámetros generales
N_COMERCIOS = 250
N_TRANSACCIONES = 18000
FECHA_FIN = datetime(2026, 11, 15, 23, 59, 59)
FECHA_INICIO = FECHA_FIN - timedelta(days=90)

# 1. GENERACIÓN DE DIMENSIÓN: DIM_COMERCIOS
rubros = ['Supermercados', 'Gastronomía', 'Farmacias', 'Indumentaria', 'E-commerce', 'Estaciones de Servicio']
pesos_rubros = [0.25, 0.25, 0.15, 0.15, 0.10, 0.10]

departamentos = ['Montevideo', 'Canelones', 'Maldonado', 'Colonia', 'Salto', 'Paysandú']
pesos_deptos = [0.55, 0.18, 0.12, 0.06, 0.05, 0.04]

tamanos = ['Pequeño', 'Mediano', 'Grande']
pesos_tamanos = [0.60, 0.30, 0.10]

comercios_data = []
for i in range(1, N_COMERCIOS + 1):
    merchant_id = f"MCH-{i:04d}"
    rubro = np.random.choice(rubros, p=pesos_rubros)
    depto = np.random.choice(departamentos, p=pesos_deptos)
    tamano = np.random.choice(tamanos, p=pesos_tamanos)
    
    # Canal principal según rubro
    if rubro == 'E-commerce':
        canal_asignado = np.random.choice(['E-commerce Gateway', 'Link de Pago'], p=[0.7, 0.3])
    else:
        canal_asignado = np.random.choice(['POS Físico', 'Smart POS'], p=[0.45, 0.55])
        
    comercios_data.append({
        'merchant_id': merchant_id,
        'nombre_comercio': f"Comercio_{rubro[:4].upper()}_{i:03d}",
        'rubro': rubro,
        'departamento': depto,
        'tamano_comercio': tamano,
        'canal_principal': canal_asignado,
        'fecha_alta': (FECHA_INICIO - timedelta(days=random.randint(30, 700))).strftime('%Y-%m-%d')
    })

df_comercios = pd.DataFrame(comercios_data)

# 2. GENERACIÓN DE HECHOS: FACT_TRANSACCIONES
sellos = ['Visa', 'Mastercard', 'Oca', 'Cabal', 'American Express']
pesos_sellos = [0.48, 0.32, 0.12, 0.05, 0.03]

# Generar timestamps con estacionalidad (picos días 1-5 y fines de semana)
timestamps = []
while len(timestamps) < N_TRANSACCIONES:
    random_seconds = random.randint(0, int((FECHA_FIN - FECHA_INICIO).total_seconds()))
    dt = FECHA_INICIO + timedelta(seconds=random_seconds)
    
    # Probabilidad de aceptar la fecha según estacionalidad
    prob_aceptar = 0.6
    if 1 <= dt.day <= 5:  # Días de cobro de sueldos
        prob_aceptar += 0.3
    if dt.weekday() >= 4:  # Viernes, Sábado, Domingo
        prob_aceptar += 0.25
    if 9 <= dt.hour <= 21: # Horario comercial
        prob_aceptar += 0.2
    else:
        prob_aceptar -= 0.45
        
    if random.random() < min(prob_aceptar, 1.0):
        timestamps.append(dt)

timestamps.sort()

# Muestreo ponderado de comercios (los grandes transaccionan más)
pesos_actividad = df_comercios['tamano_comercio'].map({'Pequeño': 1, 'Mediano': 3, 'Grande': 8}).values
pesos_actividad = pesos_actividad / pesos_actividad.sum()
comercios_seleccionados = df_comercios.sample(n=N_TRANSACCIONES, replace=True, weights=pesos_actividad).reset_index(drop=True)

# Montos realistas en UYU según rubro
tickets_medios = {
    'Supermercados': (1400, 900),
    'Gastronomía': (1100, 650),
    'Farmacias': (850, 500),
    'Indumentaria': (2400, 1300),
    'E-commerce': (2900, 1800),
    'Estaciones de Servicio': (1800, 800)
}

transacciones_data = []
fecha_corte_anomalia = FECHA_FIN - timedelta(days=3)

for idx in range(N_TRANSACCIONES):
    tx_id = f"TX-{100000 + idx}"
    dt = timestamps[idx]
    comercio = comercios_seleccionados.iloc[idx]
    
    sello = np.random.choice(sellos, p=pesos_sellos)
    
    # Oca y Amex operan principalmente como crédito
    if sello in ['Oca', 'American Express']:
        tipo_tarjeta = 'Crédito'
    else:
        tipo_tarjeta = np.random.choice(['Débito', 'Crédito'], p=[0.62, 0.38])
        
    # Cuotas y arancel base (estructura realista de adquirencia)
    if tipo_tarjeta == 'Débito':
        cuotas = 1
        arancel_pct = round(np.random.uniform(0.010, 0.013), 4) # ~1.1%
    else:
        cuotas = np.random.choice([1, 2, 3, 6, 12], p=[0.45, 0.15, 0.20, 0.12, 0.08])
        arancel_pct = round(np.random.uniform(0.025, 0.032), 4) # ~2.8%
        
    # Cálculo de monto en UYU (distribución log-normal para evitar negativos y tener cola derecha)
    media, desv = tickets_medios[comercio['rubro']]
    monto = round(max(120.0, np.random.normal(media, desv)), 2)
    if tipo_tarjeta == 'Crédito' and cuotas > 1:
        monto = round(monto * np.random.uniform(1.3, 2.2), 2)
        
    # Lógica de Estado de Transacción + INYECCIÓN DE ANOMALÍA OPERATIVA
    es_anomalia_red = (
        dt >= fecha_corte_anomalia and 
        comercio['departamento'] == 'Canelones' and 
        comercio['canal_principal'] == 'Smart POS'
    )
    
    if es_anomalia_red:
        # Falla masiva de conectividad en Smart POS en Canelones los últimos 3 días
        estado = np.random.choice(
            ['Aprobada', 'Rechazada - Fondos Insuficientes', 'Rechazada - Error Red/POS', 'Rechazada - Timeout'],
            p=[0.52, 0.08, 0.30, 0.10]
        )
    else:
        # Comportamiento normal de la red (~92% aprobación)
        estado = np.random.choice(
            ['Aprobada', 'Rechazada - Fondos Insuficientes', 'Rechazada - Error Red/POS', 'Rechazada - Timeout'],
            p=[0.92, 0.05, 0.02, 0.01]
        )
        
    transacciones_data.append({
        'transaction_id': tx_id,
        'timestamp': dt.strftime('%Y-%m-%d %H:%M:%S'),
        'merchant_id': comercio['merchant_id'],
        'canal': comercio['canal_principal'],
        'sello': sello,
        'tipo_tarjeta': tipo_tarjeta,
        'cuotas': cuotas,
        'monto_uyu': monto,
        'arancel_pct': arancel_pct,
        'estado': estado
    })

df_tx = pd.DataFrame(transacciones_data)

# 3. INYECCIÓN DE PROBLEMA DE CALIDAD DE DATOS (15 registros duplicados para auditar en SQL)
duplicados = df_tx.sample(n=15, random_state=42)
df_tx = pd.concat([df_tx, duplicados], ignore_index=True)

# Exportar a CSV
df_comercios.to_csv('dim_comercios.csv', index=False, encoding='utf-8')
df_tx.to_csv('fact_transacciones.csv', index=False, encoding='utf-8')

print(f"Generación exitosa:")
print(f"- dim_comercios.csv: {len(df_comercios)} registros")
print(f"- fact_transacciones.csv: {len(df_tx)} registros (incluye 15 duplicados intencionales para auditoría SQL)")

