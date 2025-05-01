from rest_framework import serializers
from .models import Local, Usuario, Tarea, Jornada
from django.utils import timezone

class LocalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Local
        fields = ['id', 'nombre', 'direccion']
        read_only_fields = ['id']

class UsuarioSerializer(serializers.ModelSerializer):
    local = LocalSerializer(read_only=True)
    local_id = serializers.PrimaryKeyRelatedField(
        queryset=Local.objects.all(),
        source='local',
        write_only=True,
        required=False
    )

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'local', 'local_id', 'rol', 'is_active', 'date_joined'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'is_active': {'read_only': True},
            'date_joined': {'read_only': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

class TareaSerializer(serializers.ModelSerializer):
    estado = serializers.SerializerMethodField()
    
    class Meta:
        model = Tarea
        fields = ['id', 'titulo', 'descripcion', 'fecha', 'asignado_a', 'estado']
    
    def get_estado(self, obj):
        if obj.fecha < timezone.now().date():
            return "Atrasada"
        return "Pendiente"


class JornadaSerializer(serializers.ModelSerializer):
    trabajador = UsuarioSerializer(read_only=True)
    trabajador_id = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(),
        source='trabajador',
        write_only=True
    )

    class Meta:
        model = Jornada
        fields = [
            'id', 'trabajador', 'trabajador_id',
            'fecha', 'hora_inicio', 'hora_fin'
        ]
        read_only_fields = ['id']