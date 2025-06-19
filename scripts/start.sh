#!/bin/bash

set -e  # Stop script if any error occurs

banner() {
  echo ""
  echo "==================================================="
  echo "$1"
  echo "==================================================="
  echo ""
}

banner "INSTALACIÓN DE UV"
pip3 install uv

banner "MIGRACIONES DE DJANGO"
# Generar migraciones para todas las apps
uv run manage.py makemigrations

# Aplicar todas las migraciones (BD limpia, sin conflictos)
echo "Aplicando migraciones en base de datos limpia..."
uv run manage.py migrate

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
uv run manage.py test welp_desk.tests --verbosity 2

banner "INICIANDO GUNICORN"
exec uv run gunicorn -b 0.0.0.0:8080 project.wsgi --log-level info --access-logfile - --error-logfile - 