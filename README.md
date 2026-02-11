# 📊 NYSE Stock Scanner - Investment Opportunity Detection Agent

Sistema automatizado para detectar oportunidades de inversión en acciones del NYSE basado en análisis de dispersión de la Media Móvil Simple (SMA).

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🎯 Características

- 📈 Análisis de 20 acciones del NYSE configurables
- 📊 Cálculo de SMA-29 y dispersión porcentual
- 🎨 Generación de gráficos individuales para cada acción
- 📧 Alertas automáticas por email
- ⏰ Ejecución programada diaria
- 🔔 Señales de BUY/SELL/HOLD basadas en umbrales
- 📝 Logs detallados de todas las operaciones

## 🚀 Instalación

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/TU_USUARIO/fin_agent.git
cd fin_agent
```

### Paso 2: Crear Entorno Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Configurar Email

1. Copia el archivo de ejemplo:
   ```bash
   copy .env.example .env
   ```

2. Edita el archivo `.env` con tus credenciales:
   ```env
   EMAIL_SENDER=tu_email@gmail.com
   EMAIL_PASSWORD=tu_app_password
   EMAIL_RECIPIENT=destinatario@gmail.com
   ```

3. **Importante:** Para Gmail, necesitas crear un [App Password](https://myaccount.google.com/apppasswords)

## 📖 Uso

### Ejecución Básica

```bash
# Análisis completo y envío de email
python main.py

# Modo test (3 acciones, sin email)
python main.py --test

# Solo análisis, sin email
python main.py --no-email

# Probar configuración de email
python main.py --test-email
```

### Generar Gráficos

```bash
# Análisis + gráficos
python main.py --charts

# Test con gráficos
python main.py --test --charts

# Carpeta personalizada
python main.py --charts --charts-dir mi_carpeta
```

### Acciones Específicas

```bash
# Analizar solo estas acciones
python main.py --tickers AAPL,TSLA,NVDA,GOOGL

# Con gráficos
python main.py --tickers AAPL,MSFT --charts
```

### Ejecución Programada

```bash
# Ejecutar diariamente a las 9:00 AM
python scheduler.py

# Personalizar hora (14:30)
python scheduler.py --time 14:30

# Ejecutar ahora y luego programar
python scheduler.py --run-now

# Ejecutar una sola vez
python scheduler.py --once
```

### Windows Task Scheduler

Para ejecución automática en Windows:

```bash
# Crear tarea programada (requiere permisos admin)
create_windows_task.bat

# Eliminar tarea programada
delete_windows_task.bat
```

## ⚙️ Configuración

Edita `config.py` para personalizar:

```python
# Acciones a monitorear (hasta 20)
TICKERS = [
    "AAPL", "MSFT", "GOOGL", "VIST", "META",
    "NVDA", "TSLA", "JPM", "V", "MU",
    # ... más acciones
]

# Período de la Media Móvil Simple
SMA_PERIOD = 29  # días

# Umbral de dispersión para alertas
DISPERSION_THRESHOLD = 15.0  # porcentaje

# Días de datos históricos
LOOKBACK_DAYS = 60  # días
```

## 🎨 Ejemplo de Gráficos

Cada gráfico generado incluye:
- **Panel Superior:** Precio vs SMA con áreas coloreadas
- **Panel Medio:** Dispersión porcentual con zonas de BUY/SELL
- **Panel Inferior:** Señal actual (BUY/SELL/HOLD)

## 📊 Lógica de Señales

| Condición | Señal | Interpretación |
|-----------|-------|----------------|
| Dispersión ≤ -15% | **BUY** | Precio muy por debajo de SMA |
| Dispersión ≥ +15% | **SELL** | Precio muy por encima de SMA |
| -15% < Dispersión < +15% | **HOLD** | Precio cerca de SMA |

## 📁 Estructura del Proyecto

```
fin_agent/
├── main.py                      # Script principal
├── config.py                    # Configuración
├── dispersion_scanner.py        # Lógica de análisis
├── email_alerts.py              # Sistema de emails
├── visualization.py             # Generación de gráficos
├── scheduler.py                 # Programación automática
├── requirements.txt             # Dependencias
├── .env.example                 # Ejemplo de configuración
├── README.md                    # Este archivo
├── CONFIGURACION_ACTUAL.md      # Documentación de config
├── GUIA_PROGRAMACION_DIARIA.md  # Guía de scheduling
└── README_CHARTS.md             # Documentación de gráficos
```

## 🛠️ Tecnologías

- **Python 3.8+**
- **yfinance** - Descarga de datos del mercado
- **pandas** - Análisis de datos
- **matplotlib** - Visualización
- **schedule** - Programación de tareas
- **python-dotenv** - Gestión de variables de entorno

## 📧 Alertas por Email

El sistema envía emails HTML con:
- Resumen ejecutivo de oportunidades
- Tabla de todas las acciones analizadas
- Señales de BUY/SELL/HOLD
- Métricas detalladas (precio, SMA, dispersión)

## 📝 Logs

Los logs se guardan en:
- `dispersion_scanner.log` - Log principal del scanner
- `scheduler.log` - Log del sistema de scheduling

## ⚠️ Disclaimer

**Este software es solo para fines informativos y educativos.**

- No constituye asesoría financiera
- No garantiza resultados de inversión
- Los datos pueden tener retrasos
- Siempre realiza tu propia investigación antes de invertir
- El autor no se hace responsable por pérdidas financieras

## 🤝 Contribuciones

Las contribuciones son bienvenidas:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 👨‍💻 Autor

**N. Felix**

## 🙏 Agradecimientos

- Yahoo Finance por los datos de mercado
- Comunidad de Python por las excelentes librerías

---

⭐ Si este proyecto te resulta útil, considera darle una estrella en GitHub!
