from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Certificate
import os


@receiver(post_delete, sender=Certificate)
def delete_certificate_image(sender, instance, **kwargs):
    # Проверяем, есть ли файл изображения
    if instance.image and os.path.isfile(instance.image.path):
        # Удаляем файл
        os.remove(instance.image.path)
