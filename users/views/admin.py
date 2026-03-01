# users/views/admin.py
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import User
from users.serializers.admin import UserAdminListSerializer, UserAdminWriteSerializer


class UserAdminViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    permission_classes = (IsAdminUser,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering_fields = ('date_joined', 'username', 'email', 'last_login')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserAdminListSerializer
        return UserAdminWriteSerializer
