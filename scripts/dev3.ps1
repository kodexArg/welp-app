#!/usr/bin/env pwsh

param(
    [switch]$Vite,
    [switch]$Help
)

if ($Help) {
    Write-Host "🚀 Script de desarrollo local" -ForegroundColor Green
    Write-Host ""
    Write-Host "Uso:" -ForegroundColor Yellow
    Write-Host "  .\scripts\dev.ps1                # Solo Django + Watcher"
    Write-Host "  .\scripts\dev.ps1 -Vite          # Django + Watcher + Vite"
    Write-Host "  .\scripts\dev.ps1 -Help          # Mostrar esta ayuda"
    Write-Host ""
    Write-Host "Opciones:" -ForegroundColor Yellow
    Write-Host "  -Vite    Incluir servidor Vite (http://localhost:5173)"
    Write-Host "  -Help    Mostrar esta ayuda"
    return
}

Write-Host "🚀 Iniciando desarrollo local..." -ForegroundColor Green

if ($Vite) {
    Write-Host "⚡ Iniciando servidores (Django + Vite)..." -ForegroundColor Yellow
    
    # Iniciar Vite en segundo plano
    Write-Host "🎯 Vite: http://localhost:5173" -ForegroundColor Cyan
    $viteJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        npm run dev
    }
} else {
    Write-Host "⚡ Iniciando servidor Django..." -ForegroundColor Yellow
    Write-Host "ℹ️  Para incluir Vite, usa: .\scripts\dev.ps1 -Vite" -ForegroundColor DarkGray
}

# Función para iniciar Django
function Start-DjangoServer {
    return Start-Job -ScriptBlock {
        Set-Location $using:PWD
        uv run manage.py runserver --noreload
    }
}

# Iniciar Django SIN auto-reload (--noreload)
Write-Host "🐍 Django: http://localhost:8000" -ForegroundColor Green
$djangoJob = Start-DjangoServer

# Configurar FileSystemWatcher para todo el proyecto
Write-Host "👁️  Monitoreando cambios en todo el proyecto..." -ForegroundColor Magenta

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = (Get-Location).Path
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true

# Filtros de archivos a monitorear
$watcher.Filter = "*"
$watcher.NotifyFilter = [System.IO.NotifyFilters]::LastWrite -bor [System.IO.NotifyFilters]::FileName -bor [System.IO.NotifyFilters]::DirectoryName

# Variable global para el trabajo de Django (accesible en script blocks)
$Global:CurrentDjangoJob = $djangoJob

# Acción al detectar cambios
$action = {
    $path = $Event.SourceEventArgs.FullPath
    $changeType = $Event.SourceEventArgs.ChangeType
    $fileName = Split-Path $path -Leaf
    $extension = [System.IO.Path]::GetExtension($fileName)
    
    # Filtros más específicos para evitar ruido
    $ignorePatterns = @(
        '^\..*',           # Archivos ocultos
        '.*\.tmp$',        # Archivos temporales
        '.*\.log$',        # Logs
        '__pycache__',     # Python cache
        '\.pyc$',          # Python compiled
        'node_modules',    # Node modules
        '\.git',           # Git
        'index\.lock$',    # Git index lock
        '.*\.lock$',       # Archivos de lock
        'staticfiles',     # Django static files
        '\.sqlite3$',      # SQLite database
        'venv',            # Virtual environment
        '\.venv',          # Virtual environment
        '\.env$'           # Environment files
    )
    
    $shouldIgnore = $false
    foreach ($pattern in $ignorePatterns) {
        if ($fileName -match $pattern -or $path -match $pattern) {
            $shouldIgnore = $true
            break
        }
    }
    
    if ($shouldIgnore) {
        return
    }
    
    Write-Host "🔄 Cambio detectado: $fileName ($changeType)" -ForegroundColor Yellow
    
    # Reiniciar Django
    try {
        # Detener job actual
        if ($Global:CurrentDjangoJob -and $Global:CurrentDjangoJob.State -eq 'Running') {
            Stop-Job $Global:CurrentDjangoJob -ErrorAction SilentlyContinue
            Wait-Job $Global:CurrentDjangoJob -Timeout 5 -ErrorAction SilentlyContinue
        }
        Remove-Job $Global:CurrentDjangoJob -ErrorAction SilentlyContinue
        
        Start-Sleep 1
        
        # Iniciar nuevo job
        $Global:CurrentDjangoJob = Start-Job -ScriptBlock {
            Set-Location $using:PWD
            uv run manage.py runserver --noreload
        }
        
        Write-Host "✅ Django reiniciado" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Error reiniciando Django: $_" -ForegroundColor Red
    }
}

# Registrar eventos del watcher
Register-ObjectEvent -InputObject $watcher -EventName Changed -Action $action
Register-ObjectEvent -InputObject $watcher -EventName Created -Action $action
Register-ObjectEvent -InputObject $watcher -EventName Deleted -Action $action
Register-ObjectEvent -InputObject $watcher -EventName Renamed -Action $action

Write-Host "✅ Watcher configurado - Presiona Ctrl+C para detener" -ForegroundColor Green

try {
    # Mantener el script corriendo
    while ($true) {
        Start-Sleep 1
    }
}
finally {
    # Limpieza al salir
    Write-Host "🧹 Limpiando procesos..." -ForegroundColor Yellow
    
    # Detener trabajos en segundo plano
    if ($Vite -and $viteJob) {
        Stop-Job $viteJob -ErrorAction SilentlyContinue
        Remove-Job $viteJob -ErrorAction SilentlyContinue
    }
    
    if ($Global:CurrentDjangoJob) {
        Stop-Job $Global:CurrentDjangoJob -ErrorAction SilentlyContinue
        Remove-Job $Global:CurrentDjangoJob -ErrorAction SilentlyContinue
    }
    
    # Limpiar watcher
    $watcher.EnableRaisingEvents = $false
    $watcher.Dispose()
    
    Write-Host "✅ Limpieza completada" -ForegroundColor Green
}
