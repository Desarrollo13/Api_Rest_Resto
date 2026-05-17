from rest_framework import serializers
from mesas.models import Mesa, Reserva

class MesaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mesa
        fields = ['id', 'numero', 'capacidad', 'estado']


class ReservaSerializer(serializers.ModelSerializer):
    mesa_numero = serializers.ReadOnlyField(source='mesa.numero')

    class Meta:
        model = Reserva
        fields = ['id', 'mesa', 'mesa_numero', 'cliente_nombre',
                  'cliente_telefono', 'fecha_hora', 'personas', 'confirmada']