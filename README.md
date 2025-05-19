# 📈 S&P 500 Price Simulator with GARCH and Crisis Modeling

## 📌 Descripción
Este script realiza simulaciones de precios futuros del S&P 500 utilizando:
- **Modelo EGARCH(1,1)** para volatilidad dinámica
- **Distribución t-Student** para retornos con colas pesadas
- **Eventos de crisis** con probabilidad configurable (5% por defecto)
- **Límites realistas** (mínimo 30% y máximo 300% del precio inicial)

## 🛠️ Dependencias
```python
pandas numpy matplotlib arch sklearn

📂 Estructura del Código
1. Carga de Datos

df = pd.read_csv("SP500.csv", parse_dates=["Date"])

Valida existencia de columnas Date, Close, Adj Close

Filtra datos faltantes y ordena cronológicamente

2. Modelado GARCH

modelo_garch = arch_model(df['Returns'] * 100, vol='EGarch', p=1, q=1)
Ajusta modelo EGARCH(1,1) a retornos porcentuales

Extrae volatilidad condicional para la simulación

3. Simulación Monte Carlo

for i in range(n_simulaciones):
    for j in range(dias_prediccion):
        # Lógica de simulación con crisis

Parámetros clave:

factor_crisis = 3.0 (aumento de volatilidad durante crisis)

prob_crisis = 0.05 (5% probabilidad diaria de crisis)

df_t = 4 (grados libertad para distribución t)

4. Visualización
Gráfico completo histórico + predicción

Gráfico focalizado en último año + predicción

Líneas rojas discontinuas muestran la media de simulaciones

🚀 Uso
Ejecutar el script con Python 3.8+

Ingresar:

Días a simular (ej. 30)

Número de simulaciones (ej. 1000)

Resultados:

Gráficos interactivos

Precio medio proyectado en consola

⚠️ Limitaciones
Asume que patrones históricos de volatilidad persistirán

No considera cambios macroeconómicos estructurales

Los eventos de crisis son aleatorios independientes

📊 Output Ejemplo

📅 Precio medio predicho para el último día (2023-12-15): $4765.82


> 💡 **Tip**: Para reproducir los resultados, asegúrate de tener el archivo `SP500.csv` en el mismo directorio. Los parámetros de crisis pueden ajustarse en las líneas 45-47 del código.
