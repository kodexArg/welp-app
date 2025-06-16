#!/bin/bash

set -e  # Stop script if any error occurs

banner() {
  echo ""
  echo "==================================================="
  echo "$1"
  echo "==================================================="
  echo ""
}

banner "MIGRACIONES DE DJANGO"
uv run manage.py makemigrations

# Intentar migración normal primero
if uv run manage.py migrate 2>/dev/null; then
    echo "Migraciones aplicadas exitosamente."
else
    echo "Error en migraciones detectado. Verificando si es conflicto de dependencias..."
    
    # Verificar si es el error específico de historial inconsistente
    if uv run manage.py migrate 2>&1 | grep -q "InconsistentMigrationHistory.*admin.0001_initial.*core.0001_initial"; then
        echo "Detectado conflicto de dependencias. Aplicando corrección..."
        
        # Marcar core.0001_initial como aplicada sin ejecutarla
        uv run manage.py migrate core 0001 --fake
        
        # Aplicar todas las migraciones restantes
        uv run manage.py migrate
    else
        echo "Error diferente detectado. Abortando..."
        exit 1
    fi
fi

banner "ARCHIVOS ESTÁTICOS"
uv run manage.py collectstatic --noinput

banner "VERIFICACIÓN DE SUPERUSUARIO"
if uv run manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(is_superuser=True).exists())" | grep -q "True"; then
    echo "Superusuario ya existe, omitiendo creación."
else
    uv run manage.py createsuperuser --noinput
fi

banner "PRUEBAS"
uv run manage.py test tests --verbosity 2
uv run manage.py test core.tests.test_views --verbosity 2
uv run manage.py test core.tests.test_models --verbosity 2

banner "INICIANDO GUNICORN"
exec uv run gunicorn -b 0.0.0.0:8080 project.wsgi --log-level info --access-logfile - --error-logfile - 