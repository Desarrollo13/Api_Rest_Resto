# reportes/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Sum, Count, Avg, F
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from datetime import timedelta
from ordenes.models import Orden, ItemOrden
from users.api.permissions import EsAdminOGerente


class ReporteVentasDiariasView(APIView):
    """
    Reporte de ventas del día o de una fecha específica.
    GET /api/reportes/ventas/diarias/?fecha=2024-01-15
    """
    permission_classes = [permissions.IsAuthenticated, EsAdminOGerente]

    def get(self, request):
        fecha = request.query_params.get('fecha')

        if fecha:
            try:
                from datetime import datetime
                fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Formato de fecha inválido. Use YYYY-MM-DD'},
                    status=400
                )
        else:
            fecha = timezone.now().date()

        ordenes = Orden.objects.filter(
            estado='cerrada',
            creada_en__date=fecha
        )

        total_ventas    = ordenes.aggregate(
            total=Sum('pago__total')
        )['total'] or 0

        total_ordenes   = ordenes.count()
        ticket_promedio = total_ventas / total_ordenes if total_ordenes > 0 else 0

        # Ventas por método de pago
        por_metodo = ordenes.values(
            metodo=F('pago__metodo_pago')
        ).annotate(
            cantidad=Count('id'),
            total=Sum('pago__total')
        ).order_by('-total')

        return Response({
            'fecha':           str(fecha),
            'total_ventas':    total_ventas,
            'total_ordenes':   total_ordenes,
            'ticket_promedio': round(ticket_promedio, 2),
            'por_metodo_pago': list(por_metodo),
        })


class ReporteVentasMensualesView(APIView):
    """
    Reporte de ventas de los últimos N meses.
    GET /api/reportes/ventas/mensuales/?meses=3
    """
    permission_classes = [permissions.IsAuthenticated, EsAdminOGerente]

    def get(self, request):
        meses = int(request.query_params.get('meses', 1))
        desde = timezone.now() - timedelta(days=30 * meses)

        ventas_por_mes = Orden.objects.filter(
            estado='cerrada',
            creada_en__gte=desde
        ).annotate(
            mes=TruncMonth('creada_en')
        ).values('mes').annotate(
            total_ventas=Sum('pago__total'),
            total_ordenes=Count('id'),
        ).order_by('mes')

        return Response({
            'meses_consultados': meses,
            'desde':             str(desde.date()),
            'resultados':        list(ventas_por_mes),
        })


class ReporteOrdenesporMozoView(APIView):
    """
    Reporte de órdenes y ventas por mozo.
    GET /api/reportes/mozos/?fecha=2024-01-15
    """
    permission_classes = [permissions.IsAuthenticated, EsAdminOGerente]

    def get(self, request):
        fecha = request.query_params.get('fecha')
        filtro = {'estado': 'cerrada'}

        if fecha:
            filtro['creada_en__date'] = fecha
        else:
            filtro['creada_en__date'] = timezone.now().date()

        por_mozo = Orden.objects.filter(**filtro).values(
            'mozo__id',
            'mozo__first_name',
            'mozo__last_name',
        ).annotate(
            total_ordenes=Count('id'),
            total_vendido=Sum('pago__total'),
        ).order_by('-total_vendido')

        resultados = [
            {
                'mozo_id':       r['mozo__id'],
                'nombre':        f"{r['mozo__first_name']} {r['mozo__last_name']}".strip(),
                'total_ordenes': r['total_ordenes'],
                'total_vendido': r['total_vendido'],
            }
            for r in por_mozo
        ]

        return Response({
            'fecha':      filtro['creada_en__date'],
            'resultados': resultados,
        })


class ReporteProductosMasVendidosView(APIView):
    """
    Productos más vendidos en un período.
    GET /api/reportes/productos/?dias=7
    """
    permission_classes = [permissions.IsAuthenticated, EsAdminOGerente]

    def get(self, request):
        dias  = int(request.query_params.get('dias', 7))
        top   = int(request.query_params.get('top', 10))
        desde = timezone.now() - timedelta(days=dias)

        productos = ItemOrden.objects.filter(
            orden__estado='cerrada',
            orden__creada_en__gte=desde
        ).values(
            'menu_item__id',
            'menu_item__nombre',
            'menu_item__precio',
        ).annotate(
            cantidad_vendida=Sum('cantidad'),
            total_generado=Sum(F('cantidad') * F('menu_item__precio')),
            veces_pedido=Count('id'),
        ).order_by('-cantidad_vendida')[:top]

        return Response({
            'dias_consultados': dias,
            'desde':            str(desde.date()),
            'top':              top,
            'productos':        list(productos),
        })


class ReporteResumenGeneralView(APIView):
    """
    Resumen general del día actual.
    GET /api/reportes/resumen/
    """
    permission_classes = [permissions.IsAuthenticated, EsAdminOGerente]

    def get(self, request):
        hoy = timezone.now().date()

        ordenes_hoy = Orden.objects.filter(creada_en__date=hoy)

        resumen = {
            'fecha': str(hoy),
            'ordenes': {
                'abiertas':   ordenes_hoy.filter(estado='abierta').count(),
                'en_cocina':  ordenes_hoy.filter(estado='en_cocina').count(),
                'listas':     ordenes_hoy.filter(estado='lista').count(),
                'cerradas':   ordenes_hoy.filter(estado='cerrada').count(),
                'canceladas': ordenes_hoy.filter(estado='cancelada').count(),
                'total':      ordenes_hoy.count(),
            },
            'ventas': {
                'total':          ordenes_hoy.filter(
                                    estado='cerrada'
                                  ).aggregate(t=Sum('pago__total'))['t'] or 0,
                'efectivo':       ordenes_hoy.filter(
                                    estado='cerrada',
                                    pago__metodo_pago='efectivo'
                                  ).aggregate(t=Sum('pago__total'))['t'] or 0,
                'tarjeta':        ordenes_hoy.filter(
                                    estado='cerrada',
                                    pago__metodo_pago='tarjeta'
                                  ).aggregate(t=Sum('pago__total'))['t'] or 0,
                'transferencia':  ordenes_hoy.filter(
                                    estado='cerrada',
                                    pago__metodo_pago='transferencia'
                                  ).aggregate(t=Sum('pago__total'))['t'] or 0,
            }
        }

        return Response(resumen)