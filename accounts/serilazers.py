from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    win_rate = serializers.ReadOnlyField()  # Property field
    
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'balance', 'birth_date', 
                  'total_games', 'total_wins', 'win_rate')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'email', 'birth_date')

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            birth_date=validated_data.get('birth_date')
        )
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)