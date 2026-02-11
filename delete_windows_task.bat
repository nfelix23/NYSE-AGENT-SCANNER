@echo off
REM Script para eliminar la tarea programada de Windows

echo ============================================================
echo Eliminar Tarea Programada de Windows
echo ============================================================
echo.
echo Este script eliminará la tarea programada NYSE_Stock_Scanner
echo.
pause

schtasks /delete /tn "NYSE_Stock_Scanner" /f

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo TAREA ELIMINADA EXITOSAMENTE
    echo ============================================================
) else (
    echo.
    echo ERROR: No se pudo eliminar la tarea
    echo Verifica que la tarea existe o ejecuta como Administrador
)

echo.
pause
