from rest_framework import serializers
from .models import AIContext


class AIContextSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIContext
        fields = ['id', 'key', 'title', 'content', 'is_active', 'priority', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
