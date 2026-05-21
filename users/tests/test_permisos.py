# apps/users/tests/test_permisos.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .factories import crear_usuario

class TestPermisosMenu(TestCase):
    """Solo admin y gerente pueden modificar el menú"""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('menuitem-list')
        self.payload = {
            'nombre': 'Milanesa',
            'precio': '850.00',
            'disponible': True
        }

    def _autenticar(self, rol):
        usuario = crear_usuario(rol)
        self.client.force_authenticate(user=usuario)

    def test_administrador_puede_crear_menu_item(self):
        self._autenticar('administrador')
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_gerente_puede_crear_menu_item(self):
        self._autenticar('gerente')
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_mozo_no_puede_crear_menu_item(self):
        self._autenticar('mozo')
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cocinero_no_puede_crear_menu_item(self):
        self._autenticar('cocinero')
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cajero_no_puede_crear_menu_item(self):
        self._autenticar('cajero')
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_publico_puede_ver_el_menu(self):
        """El menú es público, no requiere autenticación"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestPermisosUsuarios(TestCase):
    """Solo el administrador puede gestionar usuarios"""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('usuario-list')

    def test_administrador_puede_ver_usuarios(self):
        admin = crear_usuario('administrador')
        self.client.force_authenticate(user=admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_gerente_no_puede_ver_usuarios(self):
        gerente = crear_usuario('gerente')
        self.client.force_authenticate(user=gerente)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_mozo_no_puede_ver_usuarios(self):
        mozo = crear_usuario('mozo')
        self.client.force_authenticate(user=mozo)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)