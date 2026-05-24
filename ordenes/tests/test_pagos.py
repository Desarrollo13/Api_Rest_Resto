# ordenes/tests/test_pagos.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.tests.factories import crear_usuario
from mesas.models import Mesa
from menu.models import Categoria, MenuItem
from ordenes.models import Orden, ItemOrden
from decimal import Decimal

class TestPagos(TestCase):

    def setUp(self):
        self.client  = APIClient()
        self.cajero  = crear_usuario('cajero',  'cajero1')
        self.mozo    = crear_usuario('mozo',    'mozo1')
        self.cocinero= crear_usuario('cocinero','cocinero1')

        self.mesa = Mesa.objects.create(numero=1, capacidad=4)
        categoria = Categoria.objects.create(nombre='Principales')
        self.item = MenuItem.objects.create(
            nombre='Milanesa', precio=850, categoria=categoria
        )
        # Orden lista para pagar
        self.orden = Orden.objects.create(
            mesa=self.mesa, mozo=self.mozo, estado='lista'
        )
        ItemOrden.objects.create(orden=self.orden, menu_item=self.item, cantidad=2)

    def _url_pagar(self):
        return reverse('orden-pagar', args=[self.orden.id])

    def _url_comprobante(self):
        return reverse('orden-comprobante', args=[self.orden.id])

    # ── Flujo exitoso ──────────────────────────────────────────────────────

    def test_cajero_puede_pagar_con_efectivo(self):
        
        self.client.force_authenticate(user=self.cajero)
        response = self.client.post(self._url_pagar(), {
            'metodo_pago':    'efectivo',
            'monto_recibido': '2000.00'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # ✅ Comparar como Decimal
        
        self.assertEqual(response.data['subtotal'], Decimal('1700.00'))

    def test_pago_efectivo_calcula_vuelto(self):
        self.client.force_authenticate(user=self.cajero)
        response = self.client.post(self._url_pagar(), {
            'metodo_pago':    'efectivo',
            'monto_recibido': '2000.00'
        }, format='json')
        self.assertEqual(response.data['vuelto'], '300.00')  # 2000 - 1700

    def test_pago_cierra_la_orden_automaticamente(self):
        self.client.force_authenticate(user=self.cajero)
        self.client.post(self._url_pagar(), {
            'metodo_pago':    'efectivo',
            'monto_recibido': '2000.00'
        }, format='json')
        self.orden.refresh_from_db()
        self.assertEqual(self.orden.estado, 'cerrada')

    def test_cajero_puede_pagar_con_tarjeta(self):
        self.client.force_authenticate(user=self.cajero)
        response = self.client.post(self._url_pagar(), {
            'metodo_pago': 'tarjeta',
            'referencia':  'TXN-123456'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_comprobante_contiene_datos_correctos(self):
        self.client.force_authenticate(user=self.cajero)
        self.client.post(self._url_pagar(), {
            'metodo_pago':    'efectivo',
            'monto_recibido': '2000.00'
        }, format='json')
        response = self.client.get(self._url_comprobante())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('numero_comprobante', response.data)
        self.assertEqual(len(response.data['items']), 1)
        self.assertEqual(response.data['mesa'], 1)

    # ── Casos límite ───────────────────────────────────────────────────────

    def test_no_se_puede_pagar_orden_no_lista(self):
        orden_abierta = Orden.objects.create(
            mesa=self.mesa, mozo=self.mozo, estado='abierta'
        )
        self.client.force_authenticate(user=self.cajero)
        response = self.client.post(
            reverse('orden-pagar', args=[orden_abierta.id]),
            {'metodo_pago': 'efectivo', 'monto_recibido': '2000.00'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_monto_insuficiente_retorna_400(self):
        self.client.force_authenticate(user=self.cajero)
        response = self.client.post(self._url_pagar(), {
            'metodo_pago':    'efectivo',
            'monto_recibido': '500.00'  # menos que 1700
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_tarjeta_sin_referencia_retorna_400(self):
        self.client.force_authenticate(user=self.cajero)
        response = self.client.post(self._url_pagar(), {
            'metodo_pago': 'tarjeta'
            # falta referencia
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_mozo_no_puede_registrar_pago(self):
        self.client.force_authenticate(user=self.mozo)
        response = self.client.post(self._url_pagar(), {
            'metodo_pago':    'efectivo',
            'monto_recibido': '2000.00'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_no_se_puede_pagar_dos_veces(self):
        self.client.force_authenticate(user=self.cajero)
        self.client.post(self._url_pagar(), {
            'metodo_pago':    'efectivo',
            'monto_recibido': '2000.00'
        }, format='json')
        # Segundo intento
        response = self.client.post(self._url_pagar(), {
            'metodo_pago':    'efectivo',
            'monto_recibido': '2000.00'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)