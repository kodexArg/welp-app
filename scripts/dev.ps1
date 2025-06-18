$componentsPath = Join-Path $PSScriptRoot "..\components"
$serverProcess = $null
$npmProcess = $null
$lastRestartTime = [DateTime]::MinValue

function Start-Server {
    $now = Get-Date
    if (($now - $lastRestartTime).TotalSeconds -lt 2) {
        return
    }
    $lastRestartTime = $now
    
    if ($serverProcess) { 
        $serverProcess.Kill()
        Start-Sleep 2
    }
    Write-Host "[Django] Limpiando cache y reiniciando servidor..." -ForegroundColor Green
    # Limpiar cache de Django
    uv run python manage.py shell -c "from django.core.cache import cache; cache.clear()" | Out-Null
    $serverProcess = Start-Process -FilePath "uv" -ArgumentList "run", "manage.py", "runserver", "--noreload" -PassThru -NoNewWindow
}

function Start-Npm {
    Write-Host "[NPM] Iniciando npm run dev..." -ForegroundColor Blue
    $npmProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "npm", "run", "dev" -PassThru -NoNewWindow
}

# Cleanup al salir
Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action { 
    if ($serverProcess) { $serverProcess.Kill() }
    if ($npmProcess) { $npmProcess.Kill() }
}

# Iniciar procesos
Start-Server
Start-Npm

# Monitorear cambios en components
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $componentsPath
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true

Register-ObjectEvent -InputObject $watcher -EventName "Changed" -Action { 
    Write-Host "[Components] Cambio detectado, reiniciando Django..." -ForegroundColor Yellow
    Start-Server 
}
Register-ObjectEvent -InputObject $watcher -EventName "Created" -Action { 
    Write-Host "[Components] Archivo creado, reiniciando Django..." -ForegroundColor Yellow
    Start-Server 
}
Register-ObjectEvent -InputObject $watcher -EventName "Deleted" -Action { 
    Write-Host "[Components] Archivo eliminado, reiniciando Django..." -ForegroundColor Yellow
    Start-Server 
}

Write-Host "Servidor en ejecución. Presiona Ctrl+C para detener." -ForegroundColor Cyan

# Mantener activo
while ($true) { Start-Sleep 1 }
