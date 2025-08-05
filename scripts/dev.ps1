# Iniciar ambos servicios simultáneamente
Write-Host "Iniciando servicios de desarrollo..." -ForegroundColor Cyan

# Iniciar npm run dev en background
Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "npm", "run", "dev" -NoNewWindow

# Iniciar Django server
Write-Host "Servidor Django iniciando..." -ForegroundColor Green
uv run manage.py runserver