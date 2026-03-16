from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Project
import os

@receiver(post_delete, sender=Project)
def delete_project_image(sender, instance, **kwargs):
    # Проверяем, есть ли файл изображения
    if instance.image and os.path.isfile(instance.image.path):
        # Удаляем файл
        os.remove(instance.image.path)
