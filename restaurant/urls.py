# restaurant/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from users.api.views import UsuarioViewSet, LogoutView
from mesas.api.views import MesaViewSet, ReservaViewSet
from menu.api.views import CategoriaViewSet, MenuItemViewSet
from ordenes.api.views import OrdenViewSet

router = DefaultRouter()
router.register('usuarios',   UsuarioViewSet,   basename='usuario')
router.register('mesas',      MesaViewSet,      basename='mesa')
router.register('reservas',   ReservaViewSet,   basename='reserva')
router.register('categorias', CategoriaViewSet, basename='categoria')
router.register('menu',       MenuItemViewSet,  basename='menuitem')
router.register('ordenes',    OrdenViewSet,     basename='orden')

urlpatterns = [
    path('admin/',              admin.site.urls),

    # Auth
    path('api/auth/token/',     TokenObtainPairView.as_view(),  name='token_obtain'),
    path('api/auth/refresh/',   TokenRefreshView.as_view(),     name='token_refresh'),
    path('api/auth/logout/',    LogoutView.as_view(),           name='logout'),

    # Endpoints
    path('api/',                include(router.urls)),

    # Documentación
    path('api/schema/',         SpectacularAPIView.as_view(),   name='schema'),
    path('api/docs/',           SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/',          SpectacularRedocView.as_view(url_name='schema'),   name='redoc'),
    
    path('api/reportes/', include('reportes.api.urls')),
]