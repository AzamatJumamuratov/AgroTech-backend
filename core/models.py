from django.db import models
from parler.models import TranslatableModel, TranslatedFields

class CompanyInfo(TranslatableModel):
    translations = TranslatedFields(
        title=models.TextField(),
        description=models.TextField(),
    )
    created_at = models.DateTimeField(auto_now_add=True)

class Certificate(models.Model):
    image = models.ImageField(upload_to='certificates/')
    caption = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class Partner(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255),
        description=models.TextField(),
    )
    is_foreign = models.BooleanField(default=False)


class ContactInfo(TranslatableModel):
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=20, blank=True)
    translations = TranslatedFields(
        address=models.CharField(max_length=255, blank=True)
    )
    created_at = models.DateTimeField(auto_now_add=True)

class SocialLink(models.Model):
    telegram = models.URLField(max_length=255, blank=True)
    instagram = models.URLField(max_length=255, blank=True)
    facebook = models.URLField(max_length=255, blank=True)
    linkedin = models.URLField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
