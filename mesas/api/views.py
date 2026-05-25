from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from mesas.models import Mesa, Reserva
from .serializers import MesaSerializer, ReservaSerializer
from users.api.permissions import EsAdminOGerente, EsMozoOCajero

class MesaViewSet(viewsets.ModelViewSet):
    queryset         = Mesa.objects.all().order_by('numero')
    serializer_class = MesaSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [permissions.IsAuthenticated(), EsAdminOGerente()]
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=['patch'], url_path='estado',
            permission_classes=[permissions.IsAuthenticated, EsAdminOGerente])
    def cambiar_estado(self, request, pk=None):
        """Cambiar el estado de una mesa manualmente"""
        mesa        = self.get_object()
        nuevo_estado = request.data.get('estado')
        estados_validos = [e[0] for e in Mesa.ESTADOS]

        if nuevo_estado not in estados_validos:
            return Response(
                {'error': f'Estado inválido. Opciones: {estados_validos}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        mesa.estado = nuevo_estado
        mesa.save()
        return Response(MesaSerializer(mesa).data)

    @action(detail=False, methods=['get'], url_path='disponibles',
            permission_classes=[permissions.IsAuthenticated])
    def disponibles(self, request):
        """Listar solo las mesas disponibles"""
        personas = request.query_params.get('personas')
        mesas    = Mesa.objects.filter(estado='disponible').order_by('numero')
        if personas:
            mesas = mesas.filter(capacidad__gte=int(personas))
        return Response(MesaSerializer(mesas, many=True).data)


class ReservaViewSet(viewsets.ModelViewSet):
    queryset         = Reserva.objects.select_related('mesa', 'creada_por').order_by('fecha_hora')
    serializer_class = ReservaSerializer

    def get_permissions(self):
        if self.action == 'destroy':
            return [permissions.IsAuthenticated(), EsAdminOGerente()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        qs     = super().get_queryset()
        fecha  = self.request.query_params.get('fecha')
        estado = self.request.query_params.get('estado')
        mesa   = self.request.query_params.get('mesa')

        if fecha:
            qs = qs.filter(fecha_hora__date=fecha)
        if estado:
            qs = qs.filter(estado=estado)
        if mesa:
            qs = qs.filter(mesa__numero=mesa)
        return qs

    @action(detail=True, methods=['patch'], url_path='confirmar',
            permission_classes=[permissions.IsAuthenticated, EsAdminOGerente])
    def confirmar(self, request, pk=None):
        """Confirmar una reserva y marcar la mesa como reservada"""
        reserva = self.get_object()

        if reserva.estado != 'pendiente':
            return Response(
                {'error': f'Solo se pueden confirmar reservas pendientes. Estado actual: {reserva.estado}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        reserva.estado      = 'confirmada'
        reserva.mesa.estado = 'reservada'
        reserva.save()
        reserva.mesa.save()
        return Response(ReservaSerializer(reserva).data)

    @action(detail=True, methods=['patch'], url_path='cancelar',
            permission_classes=[permissions.IsAuthenticated, EsAdminOGerente])
    def cancelar(self, request, pk=None):
        """Cancelar una reserva y liberar la mesa"""
        reserva = self.get_object()

        if reserva.estado == 'cancelada':
            return Response(
                {'error': 'La reserva ya está cancelada.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        reserva.estado = 'cancelada'
        reserva.save()

        # Liberar la mesa solo si no tiene otras reservas confirmadas
        otras_reservas = Reserva.objects.filter(
            mesa=reserva.mesa,
            estado='confirmada'
        ).exclude(pk=reserva.pk)

        if not otras_reservas.exists():
            reserva.mesa.estado = 'disponible'
            reserva.mesa.save()

        return Response(ReservaSerializer(reserva).data)

    @action(detail=True, methods=['patch'], url_path='completar',
            permission_classes=[permissions.IsAuthenticated, EsAdminOGerente])
    def completar(self, request, pk=None):
        """Marcar reserva como completada cuando el cliente llega"""
        reserva = self.get_object()

        if reserva.estado != 'confirmada':
            return Response(
                {'error': 'Solo se pueden completar reservas confirmadas.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        reserva.estado      = 'completada'
        reserva.mesa.estado = 'ocupada'
        reserva.save()
        reserva.mesa.save()
        return Response(ReservaSerializer(reserva).data)