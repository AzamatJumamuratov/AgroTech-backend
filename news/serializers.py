import json
import logging
from rest_framework import serializers
from parler_rest.serializers import TranslatableModelSerializer, TranslatedFieldsField
from taggit.serializers import TagListSerializerField, TaggitSerializer
from .models import News, NewsImage
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile

logger = logging.getLogger('news')

class NewsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsImage
        fields = ['id', 'image', 'caption']
        read_only_fields = ['id']

class NewsSerializer(TranslatableModelSerializer):
    images = NewsImageSerializer(many=True, required=False, read_only=True)
    new_images = serializers.ListField(
        write_only=True,
        required=False,
        allow_empty=True
    )
    translations = TranslatedFieldsField(shared_model=News)
    tags = serializers.CharField(write_only=True, required=False)
    tag_list = TagListSerializerField(source='tags', read_only=True)

    class Meta:
        model = News
        fields = [
            'id', 'translations', 'image', 'created_at', 'published_at',
            'is_announcement', 'tags', 'tag_list', 'views', 'images', 'new_images', 'youtube_url'
        ]
        read_only_fields = ['created_at', 'published_at']

    def validate_new_images(self, value):
        logger.debug(f"Validating new_images: {value}")
        logger.debug(f"new_images type: {type(value)}")
        logger.debug(f"new_images length: {len(value) if value else 0}")

        validated_data = []
        if value:
            for index, image_data in enumerate(value):
                logger.debug(f"Image data at index {index}: {image_data}")
                logger.debug(f"Image data type at index {index}: {type(image_data)}")

                if not isinstance(image_data, dict):
                    logger.error(f"Invalid image data at index {index}: expected dict, got {type(image_data)}")
                    raise serializers.ValidationError(f"Image data at index {index} must be a dictionary")

                if 'image' not in image_data:
                    logger.error(f"Missing 'image' field at index {index}")
                    raise serializers.ValidationError(f"Image field is required at index {index}")

                if not isinstance(image_data['image'], (InMemoryUploadedFile, TemporaryUploadedFile)):
                    logger.error(f"Invalid image field at index {index}: expected file, got {type(image_data['image'])}")
                    raise serializers.ValidationError(f"Image field at index {index} must be a file")

                # Валидируем через NewsImageSerializer
                serializer = NewsImageSerializer(data=image_data)
                if not serializer.is_valid():
                    logger.error(f"Image validation error at index {index}: {serializer.errors}")
                    raise serializers.ValidationError(serializer.errors)

                validated_data.append(image_data)

        logger.debug(f"Validated new_images: {validated_data}")
        return validated_data

    def create(self, validated_data):
        logger.debug("=== SERIALIZER CREATE START ===")
        logger.debug(f"validated_data keys: {list(validated_data.keys())}")
        logger.debug(f"validated_data content: {validated_data}")

        images_data = validated_data.pop('new_images', [])
        tags = validated_data.pop('tags', '')

        logger.debug(f"Extracted new_images: {len(images_data)} items")
        logger.debug(f"Extracted new_images content: {images_data}")
        logger.debug(f"Extracted tags: '{tags}'")

        instance = super().create(validated_data)
        logger.debug(f"Created news instance with ID: {instance.id}")

        if tags:
            parsed_tags = self._parse_tags(tags)
            instance.tags.set(parsed_tags)
            logger.debug(f"Set tags: {parsed_tags}")

        created_images = 0
        for i, image_data in enumerate(images_data):
            try:
                logger.debug(f"Creating image {i+1}: {list(image_data.keys())}")
                NewsImage.objects.create(news=instance, **image_data)
                created_images += 1
            except Exception as e:
                logger.error(f"Failed to create image {i+1}: {e}")
                raise serializers.ValidationError(f"Failed to create image {i+1}: {str(e)}")
        logger.debug(f"Successfully created {created_images} images")
        logger.debug("=== SERIALIZER CREATE END ===")
        return instance

    def update(self, instance, validated_data):
        logger.debug("=== SERIALIZER UPDATE START ===")
        logger.debug(f"Updating instance ID: {instance.id}")
        logger.debug(f"validated_data keys: {list(validated_data.keys())}")
        logger.debug(f"validated_data content: {validated_data}")

        request = self.context.get('request')
        logger.debug(f"Request data keys: {list(request.data.keys()) if request else 'No request'}")

        deleted_images = request.data.get('deleted_images') if request else None
        if deleted_images:
            logger.debug(f"Processing deleted_images: {deleted_images}")
            try:
                if isinstance(deleted_images, str):
                    deleted_ids = json.loads(deleted_images)
                else:
                    deleted_ids = deleted_images
                logger.debug(f"Deleting image IDs: {deleted_ids}")
                deleted_count = NewsImage.objects.filter(id__in=deleted_ids, news=instance).delete()[0]
                logger.debug(f"Successfully deleted {deleted_count} images")
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(f"Error parsing deleted_images: {e}")
                raise serializers.ValidationError({'deleted_images': 'Неверный формат данных'})

        images_data = validated_data.pop('new_images', None)
        tags = validated_data.pop('tags', None)

        logger.debug(f"Extracted new_images: {images_data}")
        logger.debug(f"Images data is None: {images_data is None}")
        logger.debug(f"Images data length: {len(images_data) if images_data else 'N/A'}")
        logger.debug(f"Extracted tags: '{tags}'")

        instance = super().update(instance, validated_data)
        logger.debug("Updated main fields")

        if tags is not None:
            parsed_tags = self._parse_tags(tags)
            instance.tags.set(parsed_tags)
            logger.debug(f"Updated tags: {parsed_tags}")

        if images_data is not None:
            logger.debug(f"Adding {len(images_data)} new images")
            created_images = 0
            for i, image_data in enumerate(images_data):
                try:
                    logger.debug(f"Creating new image {i+1}: {list(image_data.keys())}")
                    NewsImage.objects.create(news=instance, **image_data)
                    created_images += 1
                except Exception as e:
                    logger.error(f"Failed to create image {i+1}: {e}")
                    raise serializers.ValidationError(f"Failed to create image {i+1}: {str(e)}")
            logger.debug(f"Successfully created {created_images} new images")
        else:
            logger.debug("No new images to add (images_data is None)")

        logger.debug("=== SERIALIZER UPDATE END ===")
        return instance

    def _parse_tags(self, tags_string):
        if not tags_string:
            return []
        parsed = [tag.strip() for tag in tags_string.split(',') if tag.strip()]
        logger.debug(f"Parsed tags '{tags_string}' -> {parsed}")
        return parsed
