from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import News
import os

@receiver(post_delete, sender=News)
def delete_news_image(sender, instance, **kwargs):
    # Проверяем, есть ли файл изображения
    if instance.image and os.path.isfile(instance.image.path):
        # Удаляем файл
        os.remove(instance.image.path)
