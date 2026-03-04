# users/views/auth.py
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from users.serializers.register import RegisterSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer que acepta email o username"""
    
    @classmethod
    def get_token(cls, user):
        """Agregar claims personalizados al token"""
        token = super().get_token(user)
        
        # Agregar información del usuario al token
        token['username'] = user.username
        token['email'] = user.email
        token['is_staff'] = user.is_staff
        token['is_superuser'] = user.is_superuser
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        
        return token
    
    def validate(self, attrs):
        """Permitir login con email o username"""
        username = attrs.get('username')
        password = attrs.get('password')
        
        print("=" * 50)
        print("INTENTO DE LOGIN:")
        print(f"username/email recibido: {username}")
        print(f"password presente: {'Sí' if password else 'No'}")
        
        # Si parece un email, buscar el username correspondiente
        if '@' in username:
            try:
                user = User.objects.get(email=username)
                print(f"Email encontrado, username real: {user.username}")
                print(f"is_staff: {user.is_staff}, is_superuser: {user.is_superuser}")
                attrs['username'] = user.username
            except User.DoesNotExist:
                print(f"No existe usuario con email: {username}")
                # Dejar que falle la validación normal
        
        print("=" * 50)
        
        # Llamar al validador padre
        data = super().validate(attrs)
        
        # Agregar información adicional del usuario a la respuesta
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'is_staff': self.user.is_staff,
            'is_superuser': self.user.is_superuser,
        }
        
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """Vista de login personalizada que acepta email o username"""
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)
    
    def create(self, request, *args, **kwargs):
        """Override para debugging"""
        print("=" * 50)
        print("DATOS DE REGISTRO RECIBIDOS:")
        print(f"request.data: {request.data}")
        print("=" * 50)
        
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("ERRORES DE VALIDACION:")
            print(serializer.errors)
            print("=" * 50)
        
        return super().create(request, *args, **kwargs)
