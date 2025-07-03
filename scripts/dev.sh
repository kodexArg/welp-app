#!/bin/bash

# Función para cleanup al salir
cleanup() {
    echo -e "\n\033[0;33mDeteniendo servicios...\033[0m"
    # Matar procesos hijos
    jobs -p | xargs -r kill
    exit 0
}

# Configurar trap para cleanup
trap cleanup SIGINT SIGTERM

echo -e "\033[0;36mIniciando servicios de desarrollo...\033[0m"

# Iniciar npm run dev en background
echo -e "\033[0;32mServidor npm iniciando...\033[0m"
npm run dev &
NPM_PID=$!

# Esperar un momento para que npm se inicie
sleep 2

# Iniciar Django server
echo -e "\033[0;32mServidor Django iniciando...\033[0m"
uv run manage.py runserver

# Si llegamos aquí, Django se detuvo
cleanup 