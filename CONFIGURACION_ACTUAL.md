# ⚙️ Configuración Actual del Sistema

Este documento muestra la configuración activa del NYSE Stock Scanner.

## 📊 Parámetros de Análisis

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| **SMA Period** | 29 días | Período de la Media Móvil Simple |
| **Dispersion Threshold** | ±15.0% | Umbral para generar alertas de BUY/SELL |
| **Lookback Days** | 60 días | Días de datos históricos a descargar |

## 📈 Acciones Monitoreadas (20)

Las siguientes acciones se analizan diariamente:

```
1. AAPL  - Apple Inc.
2. MSFT  - Microsoft Corporation
3. GOOGL - Alphabet Inc.
4. VIST  - Vista Energy
5. META  - Meta Platforms Inc.

6. NVDA  - NVIDIA Corporation
7. TSLA  - Tesla Inc.
8. JPM   - JPMorgan Chase & Co.
9. V     - Visa Inc.
10. MU   - Micron Technology

11. WMT  - Walmart Inc.
12. NU   - Nu Holdings Ltd.
13. CRWV - CrowdVision
14. ONDS - Ondas Holdings Inc.
15. GGAL - Grupo Financiero Galicia

16. NFLX - Netflix Inc.
17. CEPU - Central Puerto
18. EDN  - Empresa Distribuidora Norte
19. BMA  - Banco Macro
20. LOMA - Loma Negra
```

## 📧 Configuración de Email

| Parámetro | Valor |
|-----------|-------|
| **SMTP Server** | smtp.gmail.com |
| **SMTP Port** | 587 |
| **Sender Email** | (configurado en .env) |
| **Recipient Email** | (configurado en .env) |

## 🎯 Lógica de Señales

### Señal de COMPRA (BUY)
- Se genera cuando: **Dispersión ≤ -15.0%**
- Significa: El precio está significativamente DEBAJO de la SMA-29
- Interpretación: Posible oportunidad de compra (precio bajo)

### Señal de VENTA (SELL)
- Se genera cuando: **Dispersión ≥ +15.0%**
- Significa: El precio está significativamente ARRIBA de la SMA-29
- Interpretación: Posible oportunidad de venta (precio alto)

### Señal de MANTENER (HOLD)
- Se genera cuando: **-15.0% < Dispersión < +15.0%**
- Significa: El precio está cerca de la SMA-29
- Interpretación: No hay señal clara, mantener posición

## 📊 Fórmulas Utilizadas

### Media Móvil Simple (SMA)
```
SMA(29) = (P₁ + P₂ + ... + P₂₉) / 29

Donde P = Precio de cierre diario
```

### Dispersión Porcentual
```
Dispersión% = ((Precio_Cierre - SMA) / SMA) × 100

Ejemplo:
- Precio = $100
- SMA = $120
- Dispersión = ((100 - 120) / 120) × 100 = -16.67%
- Señal: BUY (ya que -16.67% < -15%)
```

## 🔧 Cómo Modificar la Configuración

### Cambiar el Umbral de Dispersión

Edita el archivo `config.py`:
```python
DISPERSION_THRESHOLD = 15.0  # Cambiar este valor
```

**Ejemplos:**
- `20.0` = Más conservador (menos señales, más confiables)
- `10.0` = Más agresivo (más señales, menos confiables)

### Cambiar el Período de SMA

```python
SMA_PERIOD = 29  # Cambiar este valor
```

**Períodos comunes:**
- `20` = SMA corto (más reactivo)
- `29` = Recomendado para análisis mensual
- `50` = SMA medio
- `200` = SMA largo (más estable)

### Cambiar las Acciones Analizadas

Edita la lista `TICKERS` en `config.py`:
```python
TICKERS = [
    "AAPL", "MSFT", "GOOGL",  # Tus acciones aquí
    # ... hasta 20 (o las que quieras)
]
```

### Cambiar el Lookback Period

```python
LOOKBACK_DAYS = 60  # Días de histórico a descargar
```

**Mínimo recomendado:** 2 × SMA_PERIOD
- Si SMA = 29, entonces mínimo 58 días
- Recomendado: 60-90 días para tener buffer

## 📅 Programación Diaria

El sistema está configurado para ejecutarse automáticamente:
- **Hora:** 9:00 AM
- **Frecuencia:** Diaria (Lunes a Domingo)
- **Acciones:**
  1. Descargar datos de las 20 acciones
  2. Calcular SMA-29 y dispersión
  3. Identificar oportunidades (BUY/SELL)
  4. Generar gráficos individuales
  5. Enviar email con resumen

## 📁 Archivos de Configuración

| Archivo | Descripción |
|---------|-------------|
| `config.py` | Configuración principal (tickers, períodos, umbrales) |
| `.env` | Credenciales de email (no versionar!) |
| `CONFIGURACION_ACTUAL.md` | Este documento |

## ⚠️ Notas Importantes

1. **Disclaimer:** Este sistema es solo para información. No es asesoría financiera.
2. **Datos en Tiempo Real:** Los datos provienen de Yahoo Finance y pueden tener retraso.
3. **Horarios de Mercado:** El análisis es más útil cuando se ejecuta después del cierre del mercado.
4. **Backups:** Guarda copias de tu `.env` en un lugar seguro (no en GitHub).

## 🔄 Última Actualización

**Fecha:** 2026-02-11
**Versión:** 1.0.0
