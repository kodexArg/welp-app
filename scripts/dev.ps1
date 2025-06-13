#!/usr/bin/env pwsh

# Script simple para desarrollo local
# Uso: .\scripts\dev.ps1

# Verificar que estamos en el directorio raíz del proyecto
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath
$currentDir = Get-Location

if ($currentDir.Path -ne $projectRoot) {
    Write-Host "⚠️  Cambiando al directorio raíz: $projectRoot" -ForegroundColor Yellow
    Set-Location $projectRoot
}

# Verificar que el archivo .env existe
if (-not (Test-Path ".env")) {
    Write-Host "❌ No se encontró el archivo .env en el directorio raíz" -ForegroundColor Red
    exit 1
}

Write-Host "🚀 Iniciando desarrollo local..." -ForegroundColor Green

# Verificar que npm esté disponible
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "❌ npm no está instalado" -ForegroundColor Red
    exit 1
}

# Verificar que uv esté disponible
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "❌ uv no está instalado" -ForegroundColor Red
    exit 1
}

# Instalar dependencias de frontend
Write-Host "📦 Instalando dependencias..." -ForegroundColor Yellow
npm install

Write-Host "⚡ Iniciando servidores..." -ForegroundColor Yellow

# Iniciar Vite en segundo plano
Write-Host "🎯 Vite: http://localhost:5173" -ForegroundColor Cyan
$viteJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    npm run dev
}

# Esperar un momento y luego iniciar Django
Start-Sleep 3
Write-Host "🐍 Django: http://localhost:8000" -ForegroundColor Green

# Iniciar Django en primer plano
uv run .\manage.py runserver

# Limpiar el trabajo de Vite cuando Django se detenga
Stop-Job $viteJob -ErrorAction SilentlyContinue
Remove-Job $viteJob -ErrorAction SilentlyContinue 