from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from .models import AIContext
from .serializers import AIContextSerializer
from .services.gemini_client import generate_text


class AdminAIContextViewSet(viewsets.ModelViewSet):
    """CRUD для AI контекстов. Только для админов."""
    queryset = AIContext.objects.all()
    serializer_class = AIContextSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def generate_article(request):
    """Генерация черновика статьи через ИИ (опционально)."""
    topic = request.data.get('topic', '')
    language = request.data.get('language', 'ru')

    if not topic:
        return Response({'error': 'Укажите тему статьи.'}, status=status.HTTP_400_BAD_REQUEST)

    lang_map = {'ru': 'русском', 'en': 'English', 'uz': "o'zbek", 'kk': 'qaraqalpaq'}
    lang_name = lang_map.get(language, 'русском')

    system_prompt = (
        'Ты — профессиональный копирайтер агрокомпании AgroTech. '
        'Пиши информативные, полезные статьи для фермеров и агрономов. '
        'Статья должна быть структурированной с заголовками и подзаголовками.'
    )
    prompt = f'Напиши статью на тему: "{topic}" на {lang_name} языке.'

    try:
        article_text = generate_text(prompt, system_instruction=system_prompt)
        return Response({
            'title': topic,
            'content': article_text,
            'language': language,
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
