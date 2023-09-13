from store.models import Customer
from djoser.serializers import UserSerializer as BaseUserSerializer, UserCreateSerializer as BaseUserCreateSerializer



class UserCreateSerializer(BaseUserCreateSerializer):
    class Mata(BaseUserCreateSerializer):
        fields = ['id', 'username', 'password',
                  'email', 'first_name', 'last_name']


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer):
        fields = ['id', 'username', 'email', 'first_name', 'last_name']