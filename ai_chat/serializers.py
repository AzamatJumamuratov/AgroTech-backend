from rest_framework import serializers
from .models import ChatSession, ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'content', 'metadata', 'created_at']
        read_only_fields = ['id', 'role', 'content', 'metadata', 'created_at']


class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatSession
        fields = ['id', 'title', 'message_count', 'messages', 'created_at', 'updated_at']
        read_only_fields = ['id', 'title', 'created_at', 'updated_at']

    def get_message_count(self, obj):
        return obj.messages.count()


class ChatSessionListSerializer(serializers.ModelSerializer):
    """Лёгкая версия для списка — без сообщений."""
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatSession
        fields = ['id', 'title', 'message_count', 'created_at', 'updated_at']

    def get_message_count(self, obj):
        return obj.messages.count()


class CreateSessionSerializer(serializers.Serializer):
    """Создание чата с первым сообщением."""
    message = serializers.CharField(max_length=2000)


class SendMessageSerializer(serializers.Serializer):
    """Входные данные для отправки сообщения."""
    message = serializers.CharField(max_length=2000)


class ChatResponseSerializer(serializers.Serializer):
    """Ответ AI чата."""
    text = serializers.CharField()
    pdf_url = serializers.CharField(allow_null=True)
    sources = serializers.ListField(child=serializers.DictField())
    related_projects = serializers.ListField(child=serializers.DictField())
