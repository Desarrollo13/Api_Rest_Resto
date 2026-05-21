# apps/users/permissions.py
from rest_framework.permissions import BasePermission

class EsAdministrador(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'administrador'

class EsGerente(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'gerente'

class EsMozo(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'mozo'

class EsCocinero(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'cocinero'

class EsCajero(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'cajero'

class EsAdminOGerente(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol in ('administrador', 'gerente')

class EsMozoOCajero(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol in ('mozo', 'cajero')

class EsPuedeCrearOrden(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol in (
            'mozo', 'cajero', 'gerente', 'administrador'
        )    