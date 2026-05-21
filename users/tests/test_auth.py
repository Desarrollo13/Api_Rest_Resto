# apps/users/tests/test_auth.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .factories import crear_usuario

class TestAutenticacion(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url_token   = reverse('token_obtain')
        self.url_refresh = reverse('token_refresh')
        self.url_logout  = reverse('logout')
        self.usuario = crear_usuario('mozo', username='mozo1')

    # ── Flujo exitoso ──────────────────────────────────────────────────────

    def test_login_credenciales_correctas_retorna_tokens(self):
        response = self.client.post(self.url_token, {
            'username': 'mozo1',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_token_contiene_rol_del_usuario(self):
        response = self.client.post(self.url_token, {
            'username': 'mozo1',
            'password': 'testpass123'
        })
        # El payload del token debe incluir el rol
        self.assertEqual(response.data.get('rol'), 'mozo')

    def test_refresh_token_retorna_nuevo_access(self):
        tokens = self.client.post(self.url_token, {
            'username': 'mozo1',
            'password': 'testpass123'
        }).data
        response = self.client.post(self.url_refresh, {
            'refresh': tokens['refresh']
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_logout_invalida_el_refresh_token(self):
        tokens = self.client.post(self.url_token, {
            'username': 'mozo1',
            'password': 'testpass123'
        }).data
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
        response = self.client.post(self.url_logout, {
            'refresh': tokens['refresh']
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Intentar usar el refresh ya invalidado debe fallar
        response = self.client.post(self.url_refresh, {
            'refresh': tokens['refresh']
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ── Casos límite ───────────────────────────────────────────────────────

    def test_login_password_incorrecta_retorna_401(self):
        response = self.client.post(self.url_token, {
            'username': 'mozo1',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_usuario_inexistente_retorna_401(self):
        response = self.client.post(self.url_token, {
            'username': 'noexiste',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_request_sin_token_retorna_401(self):
        response = self.client.get(reverse('orden-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)