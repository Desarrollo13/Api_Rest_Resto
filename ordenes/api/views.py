# ordenes/api/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ordenes.models import Orden, ItemOrden,Pago
from .serializers import OrdenSerializer, CrearOrdenSerializer, ItemOrdenSerializer,PagoSerializer, CrearPagoSerializer, ComprobanteSerializer
from users.api.permissions import EsAdminOGerente, EsCocinero, EsCajero, EsMozo, EsPuedeCrearOrden
from rest_framework.permissions import BasePermission

class _SoloCajero(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.rol == 'cajero'
        )




class OrdenViewSet(viewsets.ModelViewSet):
    queryset = Orden.objects.select_related('mesa', 'mozo').prefetch_related('items__menu_item').order_by('id')

    def get_serializer_class(self):
        if self.action == 'create':
            return CrearOrdenSerializer
        return OrdenSerializer

    def get_permissions(self):
        if self.action == 'create':
            # ✅ Solo mozo, cajero, gerente y admin pueden crear órdenes
            return [permissions.IsAuthenticated(), EsPuedeCrearOrden()]
        if self.action == 'destroy':
            return [permissions.IsAuthenticated(), EsAdminOGerente()]
        if self.action == 'pagar':
            return [permissions.IsAuthenticated(), EsCajero()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.rol == 'mozo':
            return self.queryset.filter(mozo=user)
        return self.queryset

    def create(self, request, *args, **kwargs):
        # ✅ Crear con CrearOrdenSerializer pero responder con OrdenSerializer completo
        serializer = CrearOrdenSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        orden = serializer.save()
        return Response(
            OrdenSerializer(orden).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['patch'], url_path='estado',
            permission_classes=[permissions.IsAuthenticated])
    def cambiar_estado(self, request, pk=None):
        orden = self.get_object()
        nuevo_estado = request.data.get('estado')
        user = request.user

        TRANSICIONES_PERMITIDAS = {
            'mozo':          {'en_cocina'},
            'cocinero':      {'lista'},
            'cajero':        {'cerrada'},
            'gerente':       {'abierta', 'en_cocina', 'lista', 'cerrada', 'cancelada'},
            'administrador': {'abierta', 'en_cocina', 'lista', 'cerrada', 'cancelada'},
        }

        permitidos = TRANSICIONES_PERMITIDAS.get(user.rol, set())
        if nuevo_estado not in permitidos:
            return Response(
                {'error': f'Tu rol no puede establecer el estado "{nuevo_estado}"'},
                status=status.HTTP_403_FORBIDDEN
            )

        orden.estado = nuevo_estado
        orden.save()
        return Response(OrdenSerializer(orden).data)

    @action(detail=True, methods=['post'], url_path='agregar-item',
            permission_classes=[permissions.IsAuthenticated])
    def agregar_item(self, request, pk=None):
        orden = self.get_object()
        if orden.estado not in ('abierta',):
            return Response(
                {'error': 'Solo se pueden agregar items a órdenes abiertas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = ItemOrdenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(orden=orden)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    @action(detail=True, methods=['post'], url_path='pagar',
            permission_classes=[permissions.IsAuthenticated,  EsCajero])
    def pagar(self, request, pk=None):
        """
        Registra el pago de una orden y la cierra automáticamente.
        Solo el cajero puede ejecutar esta acción.
        """
        orden = self.get_object()

        serializer = CrearPagoSerializer(
            data=request.data,
            context={'orden': orden, 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        pago = serializer.save()

        return Response(
            ComprobanteSerializer(pago).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['get'], url_path='comprobante',
            permission_classes=[permissions.IsAuthenticated])
    def comprobante(self, request, pk=None):
        """
        Devuelve el comprobante de pago de una orden ya cerrada.
        """
        orden = self.get_object()

        if not hasattr(orden, 'pago'):
            return Response(
                {'error': 'Esta orden no tiene un pago registrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(ComprobanteSerializer(orden.pago).data)