# reportes/api/urls.py
from django.urls import path
from .views import (
    ReporteVentasDiariasView,
    ReporteVentasMensualesView,
    ReporteOrdenesporMozoView,
    ReporteProductosMasVendidosView,
    ReporteResumenGeneralView,
)

urlpatterns = [
    path('ventas/diarias/',   ReporteVentasDiariasView.as_view(),        name='reporte-ventas-diarias'),
    path('ventas/mensuales/', ReporteVentasMensualesView.as_view(),      name='reporte-ventas-mensuales'),
    path('mozos/',            ReporteOrdenesporMozoView.as_view(),       name='reporte-mozos'),
    path('productos/',        ReporteProductosMasVendidosView.as_view(), name='reporte-productos'),
    path('resumen/',          ReporteResumenGeneralView.as_view(),        name='reporte-resumen'),
]