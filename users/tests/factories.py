# apps/users/tests/factories.py
from django.contrib.auth import get_user_model

Usuario = get_user_model()

def crear_usuario(rol, username=None):
    """Factory helper para crear usuarios de prueba"""
    username = username or f"test_{rol}"
    return Usuario.objects.create_user(
        username=username,
        password='testpass123',
        rol=rol,
        first_name=rol.capitalize()
    )