from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from drf_yasg.views import get_schema_view
from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from users.api.views import LogoutView
from users.api.views import UsuarioViewSet
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


schema_view = get_schema_view(
   openapi.Info(
      title="Restaurante API",
      default_version='v1',
      description="Documentacion de la API del Restaurante",
      terms_of_service="",
      contact=openapi.Contact(email="cristianmesa13@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
#    permission_classes=(permissions.AllowAny,),
 )





urlpatterns = [
    path('admin/',          admin.site.urls),
    path('api/auth/token/', TokenObtainPairView.as_view(),  name='token_obtain'),
    path('api/auth/refresh/',TokenRefreshView.as_view(),    name='token_refresh'),
    path('api/',            include(router.urls)),

    path('api/auth/logout/', LogoutView.as_view(), name='logout'),

    path('api/schema/',  SpectacularAPIView.as_view(), name='schema'),
    path('docs/',    SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
    
]