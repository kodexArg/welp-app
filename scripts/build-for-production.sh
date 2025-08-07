#!/bin/bash

# Script para preparar assets del frontend para producción
# Este script debe ejecutarse antes de hacer push a la rama 'prod'

set -e  # Detener si hay algún error

echo "🚀 Preparando assets del frontend para producción..."
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "package.json" ]; then
    echo "❌ Error: No se encontró package.json. Ejecuta este script desde la raíz del proyecto."
    exit 1
fi

# Instalar dependencias si es necesario
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependencias de Node.js..."
    npm install
fi

# Limpiar build anterior
if [ -d "static/dist" ]; then
    echo "🧹 Limpiando build anterior..."
    rm -rf static/dist
fi

# Construir assets
echo "🔨 Construyendo assets del frontend..."
npm run build

# Verificar que el build fue exitoso
if [ ! -d "static/dist" ]; then
    echo "❌ Error: El build falló. No se generó el directorio static/dist/"
    exit 1
fi

echo ""
echo "✅ Assets del frontend construidos exitosamente!"
echo "📁 Los archivos están en: static/dist/"
echo "⚡ El despliegue en AppRunner será mucho más rápido ahora!"