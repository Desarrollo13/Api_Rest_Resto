from rest_framework import serializers
from ordenes.models import Orden, ItemOrden
from menu.models import MenuItem

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