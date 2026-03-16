from rest_framework import serializers
from parler_rest.serializers import TranslatableModelSerializer, TranslatedFieldsField
from .models import Project, ProjectContact, ProjectComment

class ProjectSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Project)

    class Meta:
        model = Project
        fields = ['id', 'translations', 'is_current', 'image']


class ProjectContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectContact
        fields = ['id', 'name', 'email', 'phone', 'message', 'created_at']
        read_only_fields = ['created_at']

    def validate_email(self, value):
        """Валидация email"""
        if not value:
            raise serializers.ValidationError("Email обязателен для заполнения")
        return value

    def validate_name(self, value):
        """Валидация имени"""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Имя должно содержать минимум 2 символа")
        return value.strip()

class ProjectCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectComment
        fields = ['id', 'name_project', 'comment', 'created_at']
        read_only_fields = ['created_at']

    def validate_name_project(self, value):
        """Валидация названия проекта"""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Название проекта должно содержать минимум 2 символа")
        return value.strip()

    def validate_comment(self, value):
        """Валидация комментария"""
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError("Комментарий должен содержать минимум 10 символов")
        return value.strip()

    def create(self, validated_data):
        """Создание комментария с дополнительной логикой"""
        return super().create(validated_data)
