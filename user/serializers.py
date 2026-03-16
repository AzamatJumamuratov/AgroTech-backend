from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

class AdminRegisterSerializer(serializers.ModelSerializer):
    """
    Регистрация админа
    """
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'password_confirm']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.is_staff = True  # Делаем админом
        user.save()
        return user

class AdminLoginSerializer(serializers.Serializer):
    """
    Авторизация админа
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user and user.is_staff:
                data['user'] = user
                return data
            else:
                raise serializers.ValidationError('Неверные данные или нет прав админа')
        else:
            raise serializers.ValidationError('Укажите логин и пароль')

class AdminUserSerializer(serializers.ModelSerializer):
    """
    Данные админа
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']