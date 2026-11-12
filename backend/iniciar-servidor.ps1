$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$pythonExe = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonExe)) {
    throw 'Primero prepara el entorno del servidor siguiendo README.md (Python 3.11 o superior).'
}
Write-Host 'Servidor de la demo. Conecta el teléfono a la misma red Wi-Fi.'
Write-Host 'En la app indica http://IP-DEL-PC:8000. Cierra esta ventana para detenerlo.'
& $pythonExe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
