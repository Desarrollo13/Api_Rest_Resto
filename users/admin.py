# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    # Campos que se muestran en la lista
    list_display = ['username', 'email', 'rol', 'first_name', 'last_name', 'is_active']
    list_filter  = ['rol', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']

    # Agregar los campos custom al formulario de edición
    fieldsets = UserAdmin.fieldsets + (
        ('Información del restaurante', {
            'fields': ('rol', 'telefono')
        }),
    )

    # Agregar los campos custom al formulario de creación
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información del restaurante', {
            'fields': ('rol', 'telefono')
        }),
    )