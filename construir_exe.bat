@echo off
rem Genera el ejecutable del juego con PyInstaller dentro de un entorno virtual limpio (.venv).
rem Uso:   construir_exe.bat          = dist\Isaac y el corazon de mamá.exe (un solo archivo)
rem        construir_exe.bat carpeta  = dist\Isaac y el corazon de mamá\    (carpeta, arranque mas rapido)
rem Si "python" abre la Microsoft Store, indica el interprete real:
rem        set PYTHON=C:\ruta\a\python.exe
setlocal
cd /d "%~dp0"

if /i "%~1"=="carpeta" (set ONEFILE=0) else (set ONEFILE=1)
if "%PYTHON%"=="" set PYTHON=python

if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Creando entorno virtual .venv ...
    "%PYTHON%" -m venv .venv || goto :error
)

echo [2/3] Instalando dependencias ...
".venv\Scripts\python.exe" -m pip install --upgrade pip || goto :error
".venv\Scripts\python.exe" -m pip install -r requirements-build.txt || goto :error

echo [3/3] Compilando con PyInstaller ...
".venv\Scripts\python.exe" -m PyInstaller main.spec --noconfirm --clean || goto :error

echo.
echo Listo. Revisa la carpeta dist\
exit /b 0

:error
echo.
echo La compilacion fallo. Revisa los mensajes anteriores.
exit /b 1
