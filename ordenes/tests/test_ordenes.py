# apps/ordenes/tests/test_ordenes.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.tests.factories import crear_usuario
from mesas.models import Mesa
from menu.models import Categoria, MenuItem
from ordenes.models import Orden

class TestOrdenes(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.mozo    = crear_usuario('mozo',    'mozo1')
        self.cocinero= crear_usuario('cocinero','cocinero1')
        self.cajero  = crear_usuario('cajero',  'cajero1')
        self.gerente = crear_usuario('gerente', 'gerente1')

        self.mesa = Mesa.objects.create(numero=1, capacidad=4)
        categoria = Categoria.objects.create(nombre='Principales')
        self.item = MenuItem.objects.create(
            nombre='Milanesa', precio=850, categoria=categoria
        )
        self.url_ordenes = reverse('orden-list')

    def _payload_orden(self):
        return {
            'mesa': self.mesa.id,
            'items': [{'menu_item': self.item.id, 'cantidad': 2, 'nota': ''}]
        }

    def _crear_orden(self, usuario):
        self.client.force_authenticate(user=usuario)
        return self.client.post(self.url_ordenes, self._payload_orden(), format='json')

    # ── Flujo exitoso ──────────────────────────────────────────────────────

    def test_mozo_puede_crear_orden(self):
        response = self._crear_orden(self.mozo)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['estado'], 'abierta')

    def test_orden_se_asigna_al_mozo_que_la_crea(self):
        response = self._crear_orden(self.mozo)
        self.assertEqual(response.data['mozo'], self.mozo.id)

    def test_total_orden_se_calcula_correctamente(self):
        response = self._crear_orden(self.mozo)
        orden = Orden.objects.get(id=response.data['id'])
        # 2 milanesas x $850 = $1700
        self.assertEqual(orden.total, 1700)

    def test_mozo_solo_ve_sus_propias_ordenes(self):
        mozo2 = crear_usuario('mozo', 'mozo2')
        self._crear_orden(self.mozo)   # orden del mozo1
        self._crear_orden(mozo2)       # orden del mozo2

        self.client.force_authenticate(user=self.mozo)
        response = self.client.get(self.url_ordenes)
        # mozo1 solo ve su propia orden
        self.assertEqual(response.data['count'], 1)

    def test_gerente_ve_todas_las_ordenes(self):
        mozo2 = crear_usuario('mozo', 'mozo2')
        self._crear_orden(self.mozo)
        self._crear_orden(mozo2)

        self.client.force_authenticate(user=self.gerente)
        response = self.client.get(self.url_ordenes)
        self.assertEqual(response.data['count'], 2)

    # ── Cambio de estado ───────────────────────────────────────────────────

    def test_mozo_puede_enviar_orden_a_cocina(self):
        orden_id = self._crear_orden(self.mozo).data['id']
        self.client.force_authenticate(user=self.mozo)
        response = self.client.patch(
            reverse('orden-cambiar-estado', args=[orden_id]),
            {'estado': 'en_cocina'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['estado'], 'en_cocina')

    def test_cocinero_puede_marcar_orden_lista(self):
        orden = Orden.objects.create(mesa=self.mesa, mozo=self.mozo, estado='en_cocina')
        self.client.force_authenticate(user=self.cocinero)
        response = self.client.patch(
            reverse('orden-cambiar-estado', args=[orden.id]),
            {'estado': 'lista'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['estado'], 'lista')

    def test_cajero_puede_cerrar_orden(self):
        orden = Orden.objects.create(mesa=self.mesa, mozo=self.mozo, estado='lista')
        self.client.force_authenticate(user=self.cajero)
        response = self.client.patch(
            reverse('orden-cambiar-estado', args=[orden.id]),
            {'estado': 'cerrada'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['estado'], 'cerrada')

    # ── Casos límite ───────────────────────────────────────────────────────

    def test_cocinero_no_puede_crear_orden(self):
        response = self._crear_orden(self.cocinero)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_mozo_no_puede_cerrar_orden(self):
        orden = Orden.objects.create(mesa=self.mesa, mozo=self.mozo, estado='lista')
        self.client.force_authenticate(user=self.mozo)
        response = self.client.patch(
            reverse('orden-cambiar-estado', args=[orden.id]),
            {'estado': 'cerrada'}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cajero_no_puede_enviar_orden_a_cocina(self):
        orden_id = self._crear_orden(self.mozo).data['id']
        self.client.force_authenticate(user=self.cajero)
        response = self.client.patch(
            reverse('orden-cambiar-estado', args=[orden_id]),
            {'estado': 'en_cocina'}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_no_se_pueden_agregar_items_a_orden_cerrada(self):
        orden = Orden.objects.create(mesa=self.mesa, mozo=self.mozo, estado='cerrada')
        self.client.force_authenticate(user=self.mozo)
        response = self.client.post(
            reverse('orden-agregar-item', args=[orden.id]),
            {'menu_item': self.item.id, 'cantidad': 1}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_crear_orden_con_mesa_inexistente_retorna_400(self):
        self.client.force_authenticate(user=self.mozo)
        payload = {
            'mesa': 9999,
            'items': [{'menu_item': self.item.id, 'cantidad': 1}]
        }
        response = self.client.post(self.url_ordenes, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)