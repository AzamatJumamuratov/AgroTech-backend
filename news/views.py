import json
import logging
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import News, NewsImage
from .serializers import NewsSerializer, NewsImageSerializer
from django.db import models

logger = logging.getLogger('news')

class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all().order_by('-published_at')
    serializer_class = NewsSerializer
    parser_classes = [MultiPartParser, FormParser]

    def _process_images_data(self, request_data):
        logger.debug("=== PROCESSING IMAGES DATA ===")
        logger.debug(f"All request data keys: {list(request_data.keys())}")
        logger.debug(f"Request files: {list(self.request.FILES.keys())}")

        images_data = []
        index = 0

        while True:
            image_key = f'images[{index}][image]'
            caption_key = f'images[{index}][caption]'

            if image_key not in self.request.FILES:
                break  # Прерываем, если нет больше изображений

            image_data = {
                'image': self.request.FILES[image_key],
                'caption': request_data.get(caption_key, '')
            }
            logger.debug(f"Added image data for index {index}: {image_data}")
            images_data.append(image_data)
            index += 1

        logger.debug(f"Total images found: {len(images_data)}")
        logger.debug(f"Images data content: {images_data}")
        logger.debug("=== END PROCESSING IMAGES DATA ===")
        return images_data  # ЭТО БЫЛО ПРОПУЩЕНО!

    def create(self, request, *args, **kwargs):
        logger.debug("=== CREATE START ===")
        logger.debug(f"Request data keys: {list(request.data.keys())}")
        logger.debug(f"Request files: {list(request.FILES.keys())}")

        # Создаём новый словарь вместо копии QueryDict
        data = {}

        # Обрабатываем translations
        translations_raw = request.data.get('translations')
        if translations_raw:
            if isinstance(translations_raw, str):
                try:
                    data['translations'] = json.loads(translations_raw)
                    logger.debug("Translations parsed successfully")
                except json.JSONDecodeError:
                    logger.error("Failed to parse translations JSON")
                    return Response({'translations': ['Неверный формат JSON']}, status=400)
            else:
                data['translations'] = translations_raw
            logger.debug(f"Added translations to data: {data['translations']}")

        # Обрабатываем tags
        tags = request.data.get('tags')
        if tags is not None:
            data['tags'] = tags
            logger.debug(f"Added tags: {tags}")

        # Обрабатываем YouTube URL
        youtube_url = request.data.get('youtube_url')
        if youtube_url is not None:
            data['youtube_url'] = youtube_url
            logger.debug(f"Added youtube_url: {youtube_url}")

        # Обрабатываем is_announcement
        is_announcement = request.data.get('is_announcement')
        if is_announcement is not None:
            # Преобразуем строку в boolean если нужно
            if isinstance(is_announcement, str):
                data['is_announcement'] = is_announcement.lower() in ('true', '1', 'yes')
            else:
                data['is_announcement'] = bool(is_announcement)
            logger.debug(f"Added is_announcement: {data['is_announcement']}")

        # Обрабатываем главное изображение
        if 'image' in request.FILES:
            data['image'] = request.FILES['image']
            logger.debug("Added main image to data")

        # Обрабатываем дополнительные изображения
        images_data = self._process_images_data(request.data)
        if images_data:
            data['new_images'] = images_data
            logger.debug(f"Added {len(images_data)} images to new_images")
        else:
            logger.debug("No additional images data found in request")

        logger.debug(f"Final data keys: {list(data.keys())}")

        serializer = self.get_serializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
            logger.debug("Serializer validation passed")
        except Exception as e:
            logger.error(f"Serializer validation failed: {e}")
            logger.error(f"Validation errors: {serializer.errors}")
            raise

        self.perform_create(serializer)
        logger.debug("=== CREATE END ===")
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        logger.debug("=== UPDATE START ===")
        partial = kwargs.pop('partial', False)
        logger.debug(f"Request data keys: {list(request.data.keys())}")
        logger.debug(f"Request files: {list(request.FILES.keys())}")
        logger.debug(f"Partial update: {partial}")

        # Создаём новый словарь вместо копии QueryDict
        data = {}

        # Обрабатываем translations
        translations_raw = request.data.get('translations')
        if translations_raw:
            if isinstance(translations_raw, str):
                try:
                    data['translations'] = json.loads(translations_raw)
                    logger.debug("Translations parsed successfully")
                except json.JSONDecodeError:
                    logger.error("Failed to parse translations JSON")
                    return Response({'translations': ['Неверный формат JSON']}, status=400)
            else:
                data['translations'] = translations_raw
            logger.debug(f"Updated translations: {data['translations']}")

        # Обрабатываем tags
        tags = request.data.get('tags')
        if tags is not None:
            data['tags'] = tags
            logger.debug(f"Updated tags: {tags}")

        # Обрабатываем YouTube URL
        youtube_url = request.data.get('youtube_url')
        if youtube_url is not None:
            data['youtube_url'] = youtube_url
            logger.debug(f"Updated youtube_url: {youtube_url}")

        # Обрабатываем is_announcement
        is_announcement = request.data.get('is_announcement')
        if is_announcement is not None:
            if isinstance(is_announcement, str):
                data['is_announcement'] = is_announcement.lower() in ('true', '1', 'yes')
            else:
                data['is_announcement'] = bool(is_announcement)
            logger.debug(f"Updated is_announcement: {data['is_announcement']}")

        # Обрабатываем главное изображение
        if 'image' in request.FILES:
            data['image'] = request.FILES['image']
            logger.debug("Updated main image")

        # Обрабатываем дополнительные изображения
        images_data = self._process_images_data(request.data)
        if images_data:
            data['new_images'] = images_data
            logger.debug(f"Added {len(images_data)} new images for update")
        else:
            logger.debug("No additional images data found in request")

        logger.debug(f"Final data keys: {list(data.keys())}")

        instance = self.get_object()
        logger.debug(f"Updating news instance ID: {instance.id}")

        serializer = self.get_serializer(instance, data=data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
            logger.debug("Serializer validation passed")
        except Exception as e:
            logger.error(f"Serializer validation failed: {e}")
            logger.error(f"Validation errors: {serializer.errors}")
            raise

        self.perform_update(serializer)
        logger.debug("=== UPDATE END ===")
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Увеличиваем счетчик просмотров при получении новости"""
        instance = self.get_object()
        instance.views = models.F('views') + 1
        instance.save(update_fields=['views'])
        instance.refresh_from_db()
        return super().retrieve(request, *args, **kwargs)

class NewsImageViewSet(viewsets.ModelViewSet):
    queryset = NewsImage.objects.all()
    serializer_class = NewsImageSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        """Фильтрация изображений по новости если передан параметр news_id"""
        queryset = super().get_queryset()
        news_id = self.request.query_params.get('news_id')
        if news_id:
            queryset = queryset.filter(news_id=news_id)
        return queryset
