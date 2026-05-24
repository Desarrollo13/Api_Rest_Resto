from rest_framework import serializers
from ordenes.models import Orden, ItemOrden
from menu.models import MenuItem
from ordenes.models import Pago

class ItemOrdenSerializer(serializers.ModelSerializer):
    nombre      = serializers.ReadOnlyField(source='menu_item.nombre')
    precio      = serializers.ReadOnlyField(source='menu_item.precio')
    subtotal    = serializers.ReadOnlyField()

    class Meta:
        model = ItemOrden
        fields = ['id', 'menu_item', 'nombre', 'precio', 'cantidad', 'nota', 'subtotal']


class OrdenSerializer(serializers.ModelSerializer):
    items       = ItemOrdenSerializer(many=True, read_only=True)
    total       = serializers.ReadOnlyField()
    mozo_nombre = serializers.ReadOnlyField(source='mozo.get_full_name')

    class Meta:
        model = Orden
        fields = ['id', 'mesa', 'mozo', 'mozo_nombre', 'estado',
                  'items', 'total', 'creada_en', 'actualizada']
        read_only_fields = ['mozo', 'creada_en', 'actualizada']


class CrearOrdenSerializer(serializers.ModelSerializer):
    items = ItemOrdenSerializer(many=True)

    class Meta:
        model = Orden
        fields = ['mesa', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        # El mozo se asigna automáticamente desde el request
        orden = Orden.objects.create(
            mozo=self.context['request'].user,
            **validated_data
        )
        for item_data in items_data:
            ItemOrden.objects.create(orden=orden, **item_data)
        return orden
#serializers de pago
 
# ordenes/api/serializers.py — agregá esto



class PagoSerializer(serializers.ModelSerializer):
    orden_id        = serializers.ReadOnlyField(source='orden.id')
    cajero_nombre   = serializers.ReadOnlyField(source='cajero.get_full_name')
    vuelto          = serializers.ReadOnlyField()

    class Meta:
        model  = Pago
        fields = [
            'id', 'orden_id', 'metodo_pago', 'estado',
            'total', 'monto_recibido', 'vuelto',
            'cajero', 'cajero_nombre', 'fecha', 'referencia'
        ]
        read_only_fields = ['id', 'total', 'cajero', 'fecha', 'vuelto']


class CrearPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Pago
        fields = ['metodo_pago', 'monto_recibido', 'referencia']

    def validate(self, data):
        orden = self.context['orden']

        # Solo se puede pagar una orden en estado 'lista'
        if orden.estado != 'lista':
            raise serializers.ValidationError(
                f'La orden debe estar en estado "lista" para pagar. Estado actual: "{orden.estado}"'
            )

        # Si ya tiene un pago completado, no se puede volver a pagar
        if hasattr(orden, 'pago') and orden.pago.estado == 'completado':
            raise serializers.ValidationError('Esta orden ya fue pagada.')

        # Validar monto recibido para efectivo
        if data.get('metodo_pago') == 'efectivo':
            monto = data.get('monto_recibido')
            if not monto:
                raise serializers.ValidationError(
                    {'monto_recibido': 'Este campo es requerido para pagos en efectivo.'}
                )
            if monto < orden.total:
                raise serializers.ValidationError(
                    {'monto_recibido': f'El monto recibido (${monto}) es menor al total (${orden.total}).'}
                )

        # Validar referencia para tarjeta/transferencia
        if data.get('metodo_pago') in ('tarjeta', 'transferencia'):
            if not data.get('referencia'):
                raise serializers.ValidationError(
                    {'referencia': 'Este campo es requerido para pagos con tarjeta o transferencia.'}
                )
        return data

    def create(self, validated_data):
        orden   = self.context['orden']
        cajero  = self.context['request'].user
        total   = orden.total

        # Calcular vuelto solo para efectivo
        vuelto = None
        if validated_data.get('metodo_pago') == 'efectivo':
            vuelto = validated_data['monto_recibido'] - total

        pago = Pago.objects.create(
            orden          = orden,
            cajero         = cajero,
            total          = total,
            vuelto         = vuelto,
            estado         = 'completado',
            **validated_data
        )

        # Cerrar la orden automáticamente al pagar
        orden.estado = 'cerrada'
        orden.save()

        return pago 


# ordenes/api/serializers.py — Comprobante

class ComprobanteSerializer(serializers.ModelSerializer):
    """Serializer completo para el comprobante de pago"""
    numero_comprobante  = serializers.SerializerMethodField()
    mesa                = serializers.ReadOnlyField(source='orden.mesa.numero')
    mozo                = serializers.ReadOnlyField(source='orden.mozo.get_full_name')
    cajero_nombre       = serializers.ReadOnlyField(source='cajero.get_full_name')
    items               = serializers.SerializerMethodField()
    subtotal            = serializers.ReadOnlyField(source='total')
    fecha               = serializers.DateTimeField(format='%d/%m/%Y %H:%M')

    class Meta:
        model  = Pago
        fields = [
            'numero_comprobante', 'fecha', 'mesa', 'mozo',
            'cajero_nombre', 'items', 'subtotal',
            'metodo_pago', 'monto_recibido', 'vuelto', 'referencia'
        ]

    def get_numero_comprobante(self, obj):
        return f"COMP-{obj.id:06d}"  # ej: COMP-000001

    def get_items(self, obj):
        return [
            {
                'producto':  item.menu_item.nombre,
                'cantidad':  item.cantidad,
                'precio':    item.menu_item.precio,
                'subtotal':  item.subtotal,
                'nota':      item.nota,
            }
            for item in obj.orden.items.all()
        ]
    