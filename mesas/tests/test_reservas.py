# mesas/tests/test_reservas.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from users.tests.factories import crear_usuario
from mesas.models import Mesa, Reserva

class TestReservas(TestCase):

    def setUp(self):
        self.client  = APIClient()
        self.gerente = crear_usuario('gerente', 'gerente1')
        self.mozo    = crear_usuario('mozo',    'mozo1')
        self.mesa    = Mesa.objects.create(numero=1, capacidad=4)
        self.url     = reverse('reserva-list')
        self.fecha_futura = timezone.now() + timedelta(days=1)

    def _payload(self, **kwargs):
        data = {
            'mesa':             self.mesa.id,
            'cliente_nombre':   'Juan Pérez',
            'cliente_telefono': '1123456789',
            'fecha_hora':       self.fecha_futura.isoformat(),
            'personas':         2,
        }
        data.update(kwargs)
        return data

    # ── Flujo exitoso ──────────────────────────────────────────────────────

    def test_mozo_puede_crear_reserva(self):
        self.client.force_authenticate(user=self.mozo)
        response = self.client.post(self.url, self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['estado'], 'pendiente')

    def test_reserva_se_asigna_al_usuario_que_la_crea(self):
        self.client.force_authenticate(user=self.mozo)
        response = self.client.post(self.url, self._payload(), format='json')
        self.assertEqual(response.data['creada_por'], self.mozo.id)

    def test_confirmar_reserva_cambia_estado_mesa(self):
        self.client.force_authenticate(user=self.mozo)
        reserva_id = self.client.post(
            self.url, self._payload(), format='json'
        ).data['id']

        self.client.force_authenticate(user=self.gerente)
        response = self.client.patch(
            reverse('reserva-confirmar', args=[reserva_id])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['estado'], 'confirmada')
        self.mesa.refresh_from_db()
        self.assertEqual(self.mesa.estado, 'reservada')

    def test_cancelar_reserva_libera_la_mesa(self):
        self.client.force_authenticate(user=self.mozo)
        reserva_id = self.client.post(
            self.url, self._payload(), format='json'
        ).data['id']

        self.client.force_authenticate(user=self.gerente)
        self.client.patch(reverse('reserva-confirmar', args=[reserva_id]))
        self.client.patch(reverse('reserva-cancelar',  args=[reserva_id]))

        self.mesa.refresh_from_db()
        self.assertEqual(self.mesa.estado, 'disponible')

    def test_completar_reserva_marca_mesa_ocupada(self):
        self.client.force_authenticate(user=self.mozo)
        reserva_id = self.client.post(
            self.url, self._payload(), format='json'
        ).data['id']

        self.client.force_authenticate(user=self.gerente)
        self.client.patch(reverse('reserva-confirmar', args=[reserva_id]))
        response = self.client.patch(
            reverse('reserva-completar', args=[reserva_id])
        )
        self.assertEqual(response.data['estado'], 'completada')
        self.mesa.refresh_from_db()
        self.assertEqual(self.mesa.estado, 'ocupada')

    def test_filtrar_mesas_disponibles(self):
        response = self.client.get(reverse('mesa-disponibles'))
        # Sin autenticar no debería funcionar
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_mesas_disponibles_filtra_por_personas(self):
        self.client.force_authenticate(user=self.mozo)
        Mesa.objects.create(numero=2, capacidad=2)
        response = self.client.get(
            reverse('mesa-disponibles'), {'personas': 3}
        )
        # Solo debe traer la mesa con capacidad >= 3 (mesa 1 con capacidad 4)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['numero'], 1)

    # ── Casos límite ───────────────────────────────────────────────────────

    def test_no_se_puede_reservar_en_fecha_pasada(self):
        self.client.force_authenticate(user=self.mozo)
        fecha_pasada = timezone.now() - timedelta(days=1)
        response = self.client.post(
            self.url,
            self._payload(fecha_hora=fecha_pasada.isoformat()),
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_se_puede_reservar_mas_personas_que_capacidad(self):
        self.client.force_authenticate(user=self.mozo)
        response = self.client.post(
            self.url,
            self._payload(personas=10),  # mesa tiene capacidad 4
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_se_puede_reservar_mesa_en_mismo_horario(self):
        self.client.force_authenticate(user=self.mozo)
        self.client.post(self.url, self._payload(), format='json')
        # Segunda reserva en el mismo horario
        response = self.client.post(self.url, self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_se_puede_confirmar_reserva_ya_confirmada(self):
        self.client.force_authenticate(user=self.mozo)
        reserva_id = self.client.post(
            self.url, self._payload(), format='json'
        ).data['id']

        self.client.force_authenticate(user=self.gerente)
        self.client.patch(reverse('reserva-confirmar', args=[reserva_id]))
        response = self.client.patch(
            reverse('reserva-confirmar', args=[reserva_id])
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)