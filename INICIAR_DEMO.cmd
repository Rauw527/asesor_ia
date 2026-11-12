@echo off
cd /d "%~dp0backend"
if not exist ".venv\Scripts\python.exe" (
  echo Falta preparar el servidor. Consulta README.md.
  pause
  exit /b 1
)
echo Facial y Moda - servidor local de pruebas
echo Deja esta ventana abierta. En el telefono usa http://IP-DEL-PC:8000
".venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000
pause
