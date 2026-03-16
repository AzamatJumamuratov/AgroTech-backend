from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Project, ProjectContact, ProjectComment
from .serializers import ProjectSerializer, ProjectContactSerializer, ProjectCommentSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    parser_classes = [MultiPartParser, FormParser]

    # def create(self, request, *args, **kwargs):
    #     data = request.data.copy()

    #     # Если translations — строка JSON (form-data), распарси
    #     if 'translations' in data and isinstance(data['translations'], str):
    #         import json
    #         try:
    #             data['translations'] = json.loads(data['translations'])
    #         except Exception as e:
    #             return Response({'translations': ['Неверный JSON']}, status=400)

    #     serializer = self.get_serializer(data=data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     return Response(serializer.data, status=201)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        self._parse_translations(data)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()
        self._parse_translations(data)

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def _parse_translations(self, data):
        """Парсит поле translations из строки JSON, если нужно."""
        import json
        if 'translations' in data and isinstance(data['translations'], str):
            try:
                data['translations'] = json.loads(data['translations'])
            except Exception:
                raise serializers.ValidationError({'translations': ['Неверный JSON']})


class ProjectContactViewSet(viewsets.ModelViewSet):
    queryset = ProjectContact.objects.all()
    serializer_class = ProjectContactSerializer
    permission_classes = [AllowAny]
    http_method_names = ['post', 'get']  # Только POST для создания и GET для админки

    def create(self, request, *args, **kwargs):
        """Создание контакта с дополнительной обработкой"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Здесь можно добавить отправку email или другую логику
        contact = serializer.save()

        return Response(
            {
                'message': 'Ваше сообщение успешно отправлено!',
                'contact_id': contact.id
            },
            status=status.HTTP_201_CREATED
        )

    def get_queryset(self):
        """Сортировка по дате создания"""
        return ProjectContact.objects.all().order_by('-created_at')

class ProjectCommentViewSet(viewsets.ModelViewSet):
    queryset = ProjectComment.objects.all()
    serializer_class = ProjectCommentSerializer
    permission_classes = [AllowAny]
    http_method_names = ['post', 'get', 'delete']

    def get_queryset(self):
        queryset = ProjectComment.objects.all().order_by('-created_at')

        # Фильтрация по названию проекта
        project_name = self.request.query_params.get('project', None)
        if project_name:
            queryset = queryset.filter(name_project__icontains=project_name)

        return queryset

    @action(detail=False, methods=['get'])
    def by_project(self, request):
        """Получить комментарии для конкретного проекта"""
        project_name = request.query_params.get('name', None)
        if not project_name:
            return Response(
                {'error': 'Параметр name обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        comments = self.get_queryset().filter(name_project__iexact=project_name)
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """Дополнительная логика при создании комментария"""
        comment = serializer.save()

        # Здесь можно добавить логику уведомлений
        # Например, отправка email администратору о новом комментарии

        return comment
