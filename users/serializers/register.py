# users/serializers/register.py
from django.contrib.auth.models import User
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    nombre = serializers.CharField(write_only=True, required=False)
    telefono = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name', 'nombre', 'telefono')
        extra_kwargs = {
            'username': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }

    def validate(self, attrs):
        """Validar y procesar datos del frontend"""
        # Si no hay username, generarlo desde el email
        if 'username' not in attrs or not attrs['username']:
            email = attrs.get('email', '')
            attrs['username'] = email.split('@')[0] if email else ''
        
        # Si hay 'nombre', dividirlo en first_name y last_name
        if 'nombre' in attrs:
            nombre_completo = attrs.pop('nombre', '').strip()
            partes = nombre_completo.split(maxsplit=1)
            if len(partes) >= 2:
                attrs['first_name'] = partes[0]
                attrs['last_name'] = partes[1]
            elif len(partes) == 1:
                attrs['first_name'] = partes[0]
                attrs['last_name'] = ''
        
        # Remover telefono si existe (no se almacena en User por defecto)
        attrs.pop('telefono', None)
        
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
