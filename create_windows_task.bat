@echo off
REM Script para crear una tarea programada en Windows
REM Ejecuta el scanner automáticamente a las 9:00 AM todos los días

echo ============================================================
echo Crear Tarea Programada de Windows
echo ============================================================
echo.
echo Este script creará una tarea programada que ejecutará
echo el NYSE Stock Scanner todos los días a las 9:00 AM
echo.
echo IMPORTANTE: Este script requiere permisos de Administrador
echo.
pause

REM Obtener la ruta del directorio actual
set "SCRIPT_DIR=%~dp0"
set "PYTHON_PATH=%SCRIPT_DIR%venv\Scripts\python.exe"
set "SCHEDULER_PATH=%SCRIPT_DIR%scheduler.py"

REM Verificar si existe el entorno virtual
if not exist "%PYTHON_PATH%" (
    echo ERROR: No se encontró el entorno virtual en %PYTHON_PATH%
    echo Por favor, crea el entorno virtual primero o ajusta la ruta
    pause
    exit /b 1
)

echo.
echo Creando tarea programada...
echo.

REM Eliminar tarea existente si existe
schtasks /query /tn "NYSE_Stock_Scanner" >nul 2>&1
if %errorlevel% equ 0 (
    echo Eliminando tarea existente...
    schtasks /delete /tn "NYSE_Stock_Scanner" /f
)

REM Crear nueva tarea programada
schtasks /create /tn "NYSE_Stock_Scanner" ^
    /tr "\"%PYTHON_PATH%\" \"%SCHEDULER_PATH%\" --once" ^
    /sc daily ^
    /st 09:00 ^
    /ru "%USERNAME%" ^
    /rl HIGHEST

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo TAREA CREADA EXITOSAMENTE
    echo ============================================================
    echo.
    echo Nombre de la tarea: NYSE_Stock_Scanner
    echo Hora de ejecución: 9:00 AM (diariamente)
    echo Usuario: %USERNAME%
    echo.
    echo Para ver la tarea:
    echo   schtasks /query /tn "NYSE_Stock_Scanner" /v /fo list
    echo.
    echo Para ejecutar la tarea manualmente ahora:
    echo   schtasks /run /tn "NYSE_Stock_Scanner"
    echo.
    echo Para eliminar la tarea:
    echo   schtasks /delete /tn "NYSE_Stock_Scanner" /f
    echo.
    echo ============================================================
) else (
    echo.
    echo ERROR: No se pudo crear la tarea programada
    echo Asegúrate de ejecutar este script como Administrador
    echo.
)

pause
