# 📅 Guía de Programación Diaria - NYSE Stock Scanner

## Configurar el Sistema para Ejecutarse Automáticamente a las 9 AM

Tienes **3 opciones** para configurar la ejecución automática diaria:

---

## ✅ OPCIÓN 1: Tarea Programada de Windows (RECOMENDADO)

Esta es la opción más confiable para Windows. La tarea se ejecuta automáticamente incluso si cierras la ventana.

### Pasos:

1. **Ejecuta el script de creación** (como Administrador):
   ```
   Clic derecho en: create_windows_task.bat
   Selecciona: "Ejecutar como administrador"
   ```

2. **Verificar que se creó correctamente**:
   - Abre el "Programador de tareas" de Windows
   - Busca la tarea: `NYSE_Stock_Scanner`
   - Deberías ver que está programada para las 9:00 AM

3. **Probar la tarea manualmente**:
   ```bash
   schtasks /run /tn "NYSE_Stock_Scanner"
   ```

4. **Ver detalles de la tarea**:
   ```bash
   schtasks /query /tn "NYSE_Stock_Scanner" /v /fo list
   ```

### Ventajas:
- ✅ Se ejecuta automáticamente en segundo plano
- ✅ No necesitas mantener una ventana abierta
- ✅ Se ejecuta aunque no estés logueado (opcional)
- ✅ Windows maneja los reintentos si hay errores

### Para eliminar la tarea:
```
Ejecutar: delete_windows_task.bat
```

---

## ✅ OPCIÓN 2: Scheduler Python (Mantener corriendo)

Usa el módulo Python `schedule` para mantener un proceso corriendo continuamente.

### Pasos:

1. **Ejecutar el scheduler** (simple):
   ```bash
   # Ejecución a las 9:00 AM (por defecto)
   python scheduler.py
   ```

2. **Personalizar la hora**:
   ```bash
   # Ejecutar a las 14:30
   python scheduler.py --time 14:30
   ```

3. **Ejecutar ahora y luego programar**:
   ```bash
   python scheduler.py --run-now
   ```

4. **Ejecutar una sola vez (sin programación)**:
   ```bash
   python scheduler.py --once
   ```

### Usando el archivo BAT:
```
Doble clic en: run_scheduler.bat
```

### Ventajas:
- ✅ Fácil de usar
- ✅ Control total desde Python
- ✅ Genera logs en `scheduler.log`

### Desventajas:
- ❌ Debes mantener la ventana/proceso corriendo
- ❌ Se detiene si cierras la sesión

---

## ✅ OPCIÓN 3: Mantener Scheduler Corriendo al Inicio de Windows

Combina la Opción 2 con inicio automático de Windows.

### Pasos:

1. **Crear un acceso directo de `run_scheduler.bat`**

2. **Mover el acceso directo a la carpeta de Inicio**:
   - Presiona `Win + R`
   - Escribe: `shell:startup`
   - Pega el acceso directo ahí

3. **Reinicia tu PC** para probar

### Ventajas:
- ✅ Se inicia automáticamente al encender la PC
- ✅ Fácil de configurar

### Desventajas:
- ❌ Verás una ventana de consola abierta
- ❌ Se detiene si cierras la ventana

---

## 🔧 Configuración Adicional

### Cambiar la hora de ejecución

**Opción 1 (Windows Task):**
```bash
# Eliminar tarea actual
schtasks /delete /tn "NYSE_Stock_Scanner" /f

# Crear nueva con diferente hora (ej: 14:30)
schtasks /create /tn "NYSE_Stock_Scanner" ^
    /tr "\"C:\ruta\a\python.exe\" \"C:\ruta\a\scheduler.py\" --once" ^
    /sc daily ^
    /st 14:30 ^
    /ru "%USERNAME%"
```

**Opción 2 (Scheduler Python):**
```bash
python scheduler.py --time 14:30
```

### Revisar los logs

Los logs se guardan en:
- `scheduler.log` - Log del scheduler
- `dispersion_scanner.log` - Log del scanner principal

### Desactivar generación de gráficos

Si quieres que el scanner diario NO genere gráficos (para ahorrar tiempo), edita `scheduler.py`:

```python
# Línea 36, cambiar:
generate_charts=True,  # a False

# Queda así:
generate_charts=False,
```

---

## 📊 Lo que hace el sistema diario:

Cuando se ejecuta automáticamente a las 9 AM:

1. ✅ Descarga datos de las acciones configuradas (48 por defecto)
2. ✅ Calcula el SMA-29 y dispersión para cada una
3. ✅ Identifica oportunidades de COMPRA y VENTA
4. ✅ Genera gráficos individuales para cada acción (opcional)
5. ✅ Envía email a tu dirección configurada con:
   - Resumen de oportunidades
   - Tabla con todas las acciones analizadas
   - Señales de BUY/SELL/HOLD
6. ✅ Guarda logs de la ejecución

---

## 🐛 Solución de Problemas

### El scanner no se ejecuta:
1. Verifica que la tarea existe: `schtasks /query /tn "NYSE_Stock_Scanner"`
2. Revisa los logs en `scheduler.log`
3. Ejecuta manualmente para ver errores: `python scheduler.py --once`

### No llega el email:
1. Verifica tu configuración de email en `.env`
2. Prueba el email manualmente: `python main.py --test-email`
3. Revisa que el App Password sea correcto

### Faltan dependencias:
```bash
# Instalar todas las dependencias
pip install -r requirements.txt
```

### Error de permisos en Windows Task:
- Ejecuta `create_windows_task.bat` como Administrador
- Clic derecho → "Ejecutar como administrador"

---

## 📝 Comandos Útiles

```bash
# Ver todas las tareas programadas
schtasks /query

# Ejecutar la tarea manualmente ahora
schtasks /run /tn "NYSE_Stock_Scanner"

# Ver logs del scheduler
type scheduler.log

# Ver últimas 20 líneas del log
powershell -command "Get-Content scheduler.log -Tail 20"

# Probar el scanner sin programación
python main.py --test

# Probar con gráficos
python main.py --test --charts
```

---

## 🎯 Recomendación

Para uso diario en Windows, usa **OPCIÓN 1: Tarea Programada de Windows**

Es la más confiable y profesional. Se ejecutará todos los días a las 9 AM sin necesidad de mantener nada abierto.
