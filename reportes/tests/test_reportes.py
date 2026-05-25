# reportes/tests/test_reportes.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from users.tests.factories import crear_usuario
from mesas.models import Mesa
from menu.models import Categoria, MenuItem
from ordenes.models import Orden, ItemOrden
from ordenes.models import Pago
from decimal import Decimal

class TestReportes(TestCase):

    def setUp(self):
        self.client  = APIClient()
        self.admin   = crear_usuario('administrador', 'admin1')
        self.gerente = crear_usuario('gerente',       'gerente1')
        self.mozo    = crear_usuario('mozo',          'mozo1')

        self.mesa = Mesa.objects.create(numero=1, capacidad=4)
        categoria = Categoria.objects.create(nombre='Principales')
        self.item1 = MenuItem.objects.create(
            nombre='Milanesa', precio=850, categoria=categoria
        )
        self.item2 = MenuItem.objects.create(
            nombre='Gaseosa', precio=200, categoria=categoria
        )

        # Crear una orden cerrada con pago
        orden = Orden.objects.create(
            mesa=self.mesa, mozo=self.mozo, estado='cerrada'
        )
        ItemOrden.objects.create(orden=orden, menu_item=self.item1, cantidad=2)
        ItemOrden.objects.create(orden=orden, menu_item=self.item2, cantidad=1)
        Pago.objects.create(
            orden=orden, cajero=self.mozo,
            metodo_pago='efectivo', estado='completado',
            total=Decimal('1900.00'), monto_recibido=Decimal('2000.00'),
            vuelto=Decimal('100.00')
        )

    # ── Permisos ───────────────────────────────────────────────────────────

    def test_mozo_no_puede_ver_reportes(self):
        self.client.force_authenticate(user=self.mozo)
        response = self.client.get(reverse('reporte-resumen'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_puede_ver_reportes(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse('reporte-resumen'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_gerente_puede_ver_reportes(self):
        self.client.force_authenticate(user=self.gerente)
        response = self.client.get(reverse('reporte-resumen'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ── Resumen general ────────────────────────────────────────────────────

    def test_resumen_contiene_campos_correctos(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse('reporte-resumen'))
        self.assertIn('ordenes', response.data)
        self.assertIn('ventas',  response.data)
        self.assertIn('fecha',   response.data)

    def test_resumen_cuenta_ordenes_cerradas(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse('reporte-resumen'))
        self.assertEqual(response.data['ordenes']['cerradas'], 1)

    def test_resumen_total_ventas_correcto(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse('reporte-resumen'))
        self.assertEqual(response.data['ventas']['total'], Decimal('1900.00'))

    # ── Ventas diarias ─────────────────────────────────────────────────────

    def test_ventas_diarias_retorna_total(self):
        self.client.force_authenticate(user=self.admin)
        hoy = timezone.now().date()
        response = self.client.get(
            reverse('reporte-ventas-diarias'),
            {'fecha': str(hoy)}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_ventas'], Decimal('1900.00'))
        self.assertEqual(response.data['total_ordenes'], 1)

    def test_ventas_diarias_fecha_invalida_retorna_400(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(
            reverse('reporte-ventas-diarias'),
            {'fecha': 'fecha-invalida'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ── Productos más vendidos ─────────────────────────────────────────────

    def test_productos_mas_vendidos_retorna_lista(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(
            reverse('reporte-productos'),
            {'dias': 7, 'top': 5}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['productos']), 2)

    def test_producto_mas_vendido_es_milanesa(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse('reporte-productos'))
        primer_producto = response.data['productos'][0]
        self.assertEqual(primer_producto['menu_item__nombre'], 'Milanesa')
        self.assertEqual(primer_producto['cantidad_vendida'], 2)

    # ── Reporte por mozo ───────────────────────────────────────────────────

    def test_reporte_mozos_retorna_datos(self):
        self.client.force_authenticate(user=self.admin)
        hoy = timezone.now().date()
        response = self.client.get(
            reverse('reporte-mozos'),
            {'fecha': str(hoy)}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['resultados']), 1)
        self.assertEqual(
            response.data['resultados'][0]['total_vendido'],
            Decimal('1900.00')
        )