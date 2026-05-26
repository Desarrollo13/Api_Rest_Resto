#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate

# Crear superusuario si no existe
python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
Usuario = get_user_model()
if not Usuario.objects.filter(username='admin').exists():
    Usuario.objects.create_superuser(
        username='root',
        password='kaiser77',
        email='cristianmesa13@gmail.com',
        rol='administrador'
    )
    print("✅ Superusuario creado")
else:
    print("⚠️ El superusuario ya existe")
EOF