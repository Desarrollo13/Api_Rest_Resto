from rest_framework import viewsets, permissions
from menu.models import Categoria, MenuItem
from .serializers import CategoriaSerializer, MenuItemSerializer
from users.api.permissions import EsAdminOGerente

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [permissions.IsAuthenticated(), EsAdminOGerente()]
        # El menú es público (app móvil puede mostrarlo sin login)
        return [permissions.AllowAny()]


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.select_related('categoria').filter(disponible=True).order_by('id')
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [permissions.IsAuthenticated(), EsAdminOGerente()]
        return [permissions.AllowAny()]