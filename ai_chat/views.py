from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import ChatSession
from .serializers import (
    ChatSessionSerializer,
    ChatSessionListSerializer,
    CreateSessionSerializer,
    SendMessageSerializer,
    ChatResponseSerializer,
)
from .services.chat_engine import process_message


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def sessions_list(request):
    """
    GET  /api/ai/chat/sessions/ — Список чатов текущего юзера
    POST /api/ai/chat/sessions/ — Создать новый чат
    """
    if request.method == 'GET':
        sessions = ChatSession.objects.filter(user=request.user)
        serializer = ChatSessionListSerializer(sessions, many=True)
        return Response(serializer.data)

    # POST — создать чат с первым сообщением
    # Body: { "message": "Что посоветуете сажать в Нукусе?" }
    input_ser = CreateSessionSerializer(data=request.data)
    if not input_ser.is_valid():
        return Response(input_ser.errors, status=status.HTTP_400_BAD_REQUEST)

    session = ChatSession.objects.create(user=request.user)
    user_message = input_ser.validated_data['message']

    try:
        result = process_message(session, user_message)
        session.refresh_from_db()

        return Response({
            'session': ChatSessionSerializer(session).data,
            'response': {
                'text': result['text'],
                'pdf_url': result.get('pdf_url'),
                'sources': result.get('sources', []),
                'related_projects': result.get('related_projects', []),
                'contact_sent': result.get('contact_sent'),
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        # Удаляем пустую сессию если AI упал
        session.delete()
        return Response(
            {'error': f'Ошибка AI: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def session_detail(request, session_id):
    """
    GET    /api/ai/chat/sessions/{id}/ — Получить чат с историей
    DELETE /api/ai/chat/sessions/{id}/ — Удалить чат
    """
    try:
        session = ChatSession.objects.get(pk=session_id, user=request.user)
    except ChatSession.DoesNotExist:
        return Response({'error': 'Чат не найден.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ChatSessionSerializer(session)
        return Response(serializer.data)

    # DELETE
    session.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request, session_id):
    """
    POST /api/ai/chat/sessions/{id}/messages/
    Body: { "message": "Что посоветуете сажать в Нукусе?" }

    Отправляет сообщение в AI чат и получает ответ.
    """
    # Проверяем что чат принадлежит юзеру
    try:
        session = ChatSession.objects.get(pk=session_id, user=request.user)
    except ChatSession.DoesNotExist:
        return Response({'error': 'Чат не найден.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = SendMessageSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user_message = serializer.validated_data['message']

    try:
        # Обрабатываем сообщение через AI движок
        result = process_message(session, user_message)

        return Response({
            'text': result['text'],
            'pdf_url': result.get('pdf_url'),
            'sources': result.get('sources', []),
            'related_projects': result.get('related_projects', []),
            'contact_sent': result.get('contact_sent'),
        })

    except Exception as e:
        return Response(
            {'error': f'Ошибка AI: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
