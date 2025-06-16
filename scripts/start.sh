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
.venv/bin/python manage.py makemigrations
# Aplicar migración inicial con --fake-initial para evitar conflictos de dependencias)
.venv/bin/python manage.py migrate --fake-initial

banner "ARCHIVOS ESTÁTICOS"
.venv/bin/python manage.py collectstatic --noinput

banner "VERIFICACIÓN DE SUPERUSUARIO"
if .venv/bin/python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(is_superuser=True).exists())" | grep -q "True"; then
    echo "Superusuario ya existe, omitiendo creación."
else
    .venv/bin/python manage.py createsuperuser --noinput
fi

banner "PRUEBAS"
.venv/bin/python manage.py test tests --verbosity 2
.venv/bin/python manage.py test core.tests.test_views --verbosity 2
.venv/bin/python manage.py test core.tests.test_models --verbosity 2

banner "INICIANDO GUNICORN"
exec .venv/bin/gunicorn -b 0.0.0.0:8080 project.wsgi --log-level info --access-logfile - --error-logfile - 