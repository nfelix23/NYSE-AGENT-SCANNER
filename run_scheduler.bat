@echo off
REM Script para ejecutar el scheduler del NYSE Stock Analyzer
REM Este script mantiene el scheduler corriendo continuamente

echo ============================================================
echo NYSE Stock Scanner - Scheduler
echo ============================================================
echo.
echo Iniciando scheduler...
echo El scanner se ejecutará automáticamente a las 09:00 diariamente
echo.
echo Presiona Ctrl+C para detener el scheduler
echo ============================================================
echo.

cd /d "%~dp0"

REM Activar el entorno virtual si existe
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    python scheduler.py
) else (
    python scheduler.py
)

pause
