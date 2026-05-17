from rest_framework import viewsets, permissions
from mesas.models import Mesa, Reserva
from .serializers import MesaSerializer, ReservaSerializer
from users.api.permissions import EsAdminOGerente, EsMozoOCajero

class MesaViewSet(viewsets.ModelViewSet):
    queryset = Mesa.objects.all()
    serializer_class = MesaSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [permissions.IsAuthenticated(), EsAdminOGerente()]
        # Mozo y cajero solo pueden ver
        return [permissions.IsAuthenticated()]


class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.select_related('mesa').all()
    serializer_class = ReservaSerializer

    def get_permissions(self):
        if self.action == 'destroy':
            return [permissions.IsAuthenticated(), EsAdminOGerente()]
        return [permissions.IsAuthenticated()]