from django.db import models
from parler.models import TranslatableModel, TranslatedFields

class Project(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(max_length=255),
        description=models.TextField(),
    )
    is_current = models.BooleanField(default=True)
    image = models.ImageField(upload_to='projects/', null=True, blank=True)

class ProjectContact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class ProjectComment(models.Model):
    name_project = models.CharField(max_length=255)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

