from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from .serializers import SearchInputSerializer, SearchResultSerializer
from ai_core.services.embeddings import search_news, search_similar


@api_view(['POST'])
@permission_classes([AllowAny])
def search_news_view(request):
    """Поиск по новостям через RAG.

    POST /api/ai/search/
    Body: { "query": "удобрения для хлопка", "language": "ru", "top_k": 5 }
    """
    serializer = SearchInputSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    query = serializer.validated_data['query']
    language = serializer.validated_data['language']
    top_k = serializer.validated_data['top_k']

    try:
        results = search_news(query, top_k=top_k, language=language)

        output = []
        for doc in results:
            # Обрезаем текст до 200 символов для сниппета
            snippet = doc.content_text[:200] + '...' if len(doc.content_text) > 200 else doc.content_text
            output.append({
                'source_type': doc.source_type,
                'source_id': doc.source_id,
                'title': doc.content_title,
                'snippet': snippet,
                'language': doc.language,
            })

        return Response({'results': output})

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def search_all_view(request):
    """Поиск по всему контенту (новости, проекты, компания и т.д.).

    POST /api/ai/search/all/
    Body: { "query": "...", "language": "ru", "top_k": 5 }
    """
    serializer = SearchInputSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    query = serializer.validated_data['query']
    language = serializer.validated_data['language']
    top_k = serializer.validated_data['top_k']

    try:
        results = search_similar(query, top_k=top_k, language=language)

        output = []
        for doc in results:
            snippet = doc.content_text[:200] + '...' if len(doc.content_text) > 200 else doc.content_text
            output.append({
                'source_type': doc.source_type,
                'source_id': doc.source_id,
                'title': doc.content_title,
                'snippet': snippet,
                'language': doc.language,
            })

        return Response({'results': output})

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
