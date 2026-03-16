from django.db import models
from parler.models import TranslatableModel, TranslatedFields
from taggit.managers import TaggableManager



class News(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(max_length=255),
        content=models.TextField(),
    )
    image = models.ImageField(upload_to='news/', blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True) 
    created_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(auto_now_add=True)
    is_announcement = models.BooleanField(default=False)
    tags = TaggableManager(blank=True)

    views = models.PositiveIntegerField(default=0)


class NewsImage(models.Model):
    news = models.ForeignKey(News, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='news/gallery/')
    caption = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.caption or f"Image for {self.news}"
