from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decouple import config

class Command(BaseCommand):
    help = 'Crea el superusuario administrador si no existe'

    def handle(self, *args, **kwargs):
        Usuario = get_user_model()
        username = config('ADMIN_USERNAME', default='root')
        password = config('ADMIN_PASSWORD', default='kaiser77')
        email    = config('ADMIN_EMAIL',    default='cristianmesa13@gmail.com')

        if not Usuario.objects.filter(username=username).exists():
            Usuario.objects.create_superuser(
                username=username,
                password=password,
                email=email,
                rol='administrador'
            )
            self.stdout.write(self.style.SUCCESS(f'✅ Admin creado: {username}'))
        else:
            self.stdout.write(f'⚠️  Ya existe: {username}')