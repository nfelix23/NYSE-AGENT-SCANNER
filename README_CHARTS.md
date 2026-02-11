# NYSE Stock Analyzer - Chart Generation Feature

## Nueva Funcionalidad: Gráficos Individuales por Stock

La aplicación ahora incluye la capacidad de generar gráficos individuales para cada stock analizado, mostrando información detallada del análisis técnico.

## Características de los Gráficos

Cada gráfico muestra:

1. **Panel Superior - Análisis de Precio:**
   - Precio de cierre histórico
   - Media Móvil Simple (SMA-29)
   - Áreas coloreadas indicando precio por encima (rojo) o debajo (verde) de la SMA
   - Punto marcado con el precio más reciente
   - Cuadro de información con valores actuales

2. **Panel Medio - Dispersión:**
   - Barras de dispersión porcentual
   - Zonas de compra (verde) y venta (rojo)
   - Líneas de umbral (+/-20%)

3. **Panel Inferior - Señal:**
   - Indicador grande con la señal actual: BUY, SELL o HOLD
   - Color codificado (verde=compra, rojo=venta, gris=mantener)

## Cómo Usar

### Opción 1: Generar gráficos con análisis completo
```bash
python main.py --charts
```
Esto ejecutará el análisis de las 20 acciones y generará un gráfico PNG para cada una en la carpeta `charts/`.

### Opción 2: Modo de prueba con gráficos
```bash
python main.py --test --charts
```
Analiza solo 3 acciones (AAPL, MSFT, GOOGL) y genera sus gráficos.

### Opción 3: Gráficos sin enviar email
```bash
python main.py --charts --no-email
```
Genera los gráficos sin enviar la alerta por email.

### Opción 4: Personalizar carpeta de salida
```bash
python main.py --charts --charts-dir mi_carpeta
```
Guarda los gráficos en una carpeta personalizada.

### Opción 5: Tickers específicos con gráficos
```bash
python main.py --tickers AAPL,TSLA,NVDA --charts
```
Analiza solo los tickers especificados y genera sus gráficos.

## Estructura de Salida

Los gráficos se guardan como archivos PNG con el siguiente formato:
```
charts/
├── AAPL_analysis.png
├── MSFT_analysis.png
├── GOOGL_analysis.png
└── ...
```

## Módulo de Visualización

El nuevo módulo `visualization.py` incluye:

- `create_stock_chart(ticker, data, period, save_path)`: Crea un gráfico individual
- `generate_all_charts(tickers, output_dir)`: Genera gráficos para múltiples tickers

## Ejemplo de Uso Programático

```python
from visualization import generate_all_charts

tickers = ["AAPL", "MSFT", "GOOGL"]
summary = generate_all_charts(tickers, output_dir="my_charts")

print(f"Generated {summary['successful']} charts")
print(f"Failed: {summary['failed']}")
```

## Requisitos

El módulo de visualización requiere:
- matplotlib (ya incluido en requirements.txt)
- pandas
- numpy

## Notas

- Los gráficos se generan con resolución de 150 DPI
- Tamaño: 14x10 pulgadas
- Formato: PNG con fondo blanco
- Fecha y hora de generación incluida en cada gráfico
