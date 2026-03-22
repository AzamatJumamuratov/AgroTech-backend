from rest_framework import serializers


class SearchInputSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=500)
    language = serializers.CharField(max_length=5, required=False, default='ru')
    top_k = serializers.IntegerField(required=False, default=5, min_value=1, max_value=20)


class SearchResultSerializer(serializers.Serializer):
    source_type = serializers.CharField()
    source_id = serializers.IntegerField()
    title = serializers.CharField()
    snippet = serializers.CharField()
    language = serializers.CharField()
