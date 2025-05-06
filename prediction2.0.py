import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
from arch import arch_model
from sklearn.metrics import mean_squared_error

# ---------------------------------------Carga de datos---------------------------------------
try:
    df = pd.read_csv("SP500.csv", parse_dates=["Date"])
    print(f"\n✅ Dataset cargado correctamente. Total de registros: {len(df)}")
except Exception as e:
    print(f"❌ Error al cargar el archivo: {e}")
    sys.exit()

required_cols = ['Date', 'Close', 'Adj Close']
if not all(col in df.columns for col in required_cols):
    print(f"❌ Faltan columnas necesarias: {required_cols}")
    sys.exit()

df = df.sort_values('Date').dropna(subset=['Adj Close'])
print(f"📊 Datos históricos desde {df['Date'].iloc[0].date()} hasta {df['Date'].iloc[-1].date()}")

# ---------------------------------------Configuración---------------------------------------
total_dias = len(df)
dias_prediccion = 100  
precio_inicial = df['Adj Close'].iloc[-1]

try:
    n_simulaciones = int(input("🔁 ¿Cuántas simulaciones deseas ejecutar?: "))
except:
    print("❌ Entrada inválida.")
    sys.exit()

print(f"\n🛠️ Ejecutando {n_simulaciones} simulaciones de {dias_prediccion} días...")

# ---------------------------------------Preprocesamiento---------------------------------------
df['Returns'] = df['Adj Close'].pct_change()
df = df.dropna()

# ---------------------------------------Ajuste de modelo GARCH---------------------------------------
print("\n⚙️ Ajustando modelo GARCH(1,1) y EGARCH...")
modelo_garch = arch_model(df['Returns'] * 100, vol='EGarch', p=1, q=1)
resultados = modelo_garch.fit(disp='off')

# Proyección de volatilidad futura (para el futuro)
volatilidad_dia_a_dia = resultados.conditional_volatility.values / 100

media = df['Returns'].mean()
print(f"📈 Media diaria de retornos: {media:.5f}")
print(f"📉 Volatilidad dinámica proyectada (primeros 5 días): {volatilidad_dia_a_dia[:5]}")

# ---------------------------------------Simulaciones con crisis estructural---------------------------------------
df_t = 4  # grados de libertad para la t-Student
factor_volatilidad = 0.75
factor_crisis = 3.0
prob_crisis = 0.05  # 5% de probabilidad de crisis diaria

limite_inferior = precio_inicial * 0.3
limite_superior = precio_inicial * 3

todas_las_simulaciones = np.zeros((n_simulaciones, dias_prediccion + 1))
crisis_marcadas = np.zeros((n_simulaciones, dias_prediccion), dtype=bool)

for i in range(n_simulaciones):
    precios = [precio_inicial]
    for j in range(dias_prediccion):
        std_dinamica = volatilidad_dia_a_dia[j] if j < len(volatilidad_dia_a_dia) else volatilidad_dia_a_dia[-1]
        std_dinamica *= factor_volatilidad

        # Modo crisis aleatorio
        crisis = np.random.rand() < prob_crisis
        if crisis:
            std_dinamica *= factor_crisis
            crisis_marcadas[i, j] = True

        # Simulación de retorno con t-Student
        t_sample = np.random.standard_t(df_t)
        retorno_simulado = media + std_dinamica * t_sample * np.sqrt((df_t - 2) / df_t)

        nuevo_precio = precios[-1] * (1 + retorno_simulado)
        nuevo_precio = min(max(nuevo_precio, limite_inferior), limite_superior)

        precios.append(nuevo_precio)
    todas_las_simulaciones[i] = precios

# Media de precios día a día
precios_medios = np.mean(todas_las_simulaciones, axis=0)

# Fechas futuras
ultima_fecha = df['Date'].iloc[-1]
fechas_futuras = pd.date_range(start=ultima_fecha + pd.Timedelta(days=1), periods=dias_prediccion + 1)

# ---------------------------------------Gráfico general---------------------------------------
plt.figure(figsize=(14, 7))
plt.plot(df['Date'], df['Adj Close'], label='Datos históricos', color='blue', alpha=0.6)
plt.plot(fechas_futuras, precios_medios, label=f'Media de {n_simulaciones} simulaciones con crisis', color='red', linestyle='--')
plt.title(f'S&P 500: Histórico + Predicción con Crisis ({dias_prediccion} días)')
plt.xlabel('Fecha')
plt.ylabel('Precio Ajustado')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# ---------------------------------------Gráfico último año + predicción---------------------------------------
plt.figure(figsize=(14, 7))
ultimo_anio = df[df['Date'] >= (df['Date'].iloc[-1] - pd.Timedelta(days=365))]
plt.plot(ultimo_anio['Date'], ultimo_anio['Adj Close'], label='Último año (histórico)', color='green')
plt.plot(fechas_futuras, precios_medios, label='Predicción (media)', color='red', linestyle='--')
plt.title(f'S&P 500: Último año + Predicción ({dias_prediccion} días, {n_simulaciones} simulaciones con crisis)')
plt.xlabel('Fecha')
plt.ylabel('Precio Ajustado')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# ---------------------------------------Precio final---------------------------------------
print(f"\n📅 Precio medio predicho para el último día ({fechas_futuras[-1].date()}): ${precios_medios[-1]:.2f}")
