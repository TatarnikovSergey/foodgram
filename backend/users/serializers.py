from djoser.serializers import UserSerializer

from .models import User


# class CustomUserSerializer(UserSerializer):
#     class Meta(UserSerializer.Meta):
#         model = User
#         fields = ('email', 'id', 'username', 'first_name', 'last_name')
