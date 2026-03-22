from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['phone', 'city']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']
        read_only_fields = ['id', 'username']


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, default='')
    password = serializers.CharField(min_length=6, write_only=True)
    first_name = serializers.CharField(max_length=150, required=False, default='')
    last_name = serializers.CharField(max_length=150, required=False, default='')
    phone = serializers.CharField(max_length=20, required=False, default='')
    city = serializers.CharField(max_length=255, required=False, default='')

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Пользователь с таким именем уже существует.')
        return value

    def create(self, validated_data):
        phone = validated_data.pop('phone', '')
        city = validated_data.pop('city', '')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )

        # Обновляем профиль (создаётся автоматически через сигнал)
        user.profile.phone = phone
        user.profile.city = city
        user.profile.save()

        return user


class UpdateProfileSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(max_length=20, required=False)
    city = serializers.CharField(max_length=255, required=False)

    def update(self, user, validated_data):
        # Обновляем поля User
        for field in ['first_name', 'last_name', 'email']:
            if field in validated_data:
                setattr(user, field, validated_data[field])
        user.save()

        # Обновляем поля UserProfile
        profile = user.profile
        for field in ['phone', 'city']:
            if field in validated_data:
                setattr(profile, field, validated_data[field])
        profile.save()

        return user
