from django.db import models
from pgvector.django import VectorField


class DocumentEmbedding(models.Model):
    """Векторные эмбеддинги контента из БД для RAG поиска."""

    source_type = models.CharField(
        max_length=50, db_index=True,
        help_text='Тип источника: news, project, company_info, partner, certificate, contact_info'
    )
    source_id = models.IntegerField(help_text='ID записи в исходной таблице')
    language = models.CharField(max_length=5, default='ru')

    # Текст, из которого сгенерирован эмбеддинг
    content_text = models.TextField()
    content_title = models.CharField(max_length=500, blank=True)

    # Векторный эмбеддинг (3072 размерность для gemini-embedding-001)
    embedding = VectorField(dimensions=3072)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['source_type', 'source_id', 'language']
        verbose_name = 'Эмбеддинг документа'
        verbose_name_plural = 'Эмбеддинги документов'

    def __str__(self):
        return f"[{self.source_type}:{self.source_id}] {self.content_title[:50]}"


class AIContext(models.Model):
    """Кастомный контекст от админа для ИИ.
    Админ добавляет инфу о компании, персонализацию и т.д.
    """

    key = models.CharField(
        max_length=100, unique=True,
        help_text='Уникальный ключ, например: company_description, agronomist_persona'
    )
    title = models.CharField(max_length=255, help_text='Название для отображения в админке')
    content = models.TextField(help_text='Текст контекста, который будет добавлен в промпт ИИ')
    is_active = models.BooleanField(default=True, help_text='Включён ли этот контекст')
    priority = models.IntegerField(default=0, help_text='Порядок в системном промпте (меньше = выше)')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['priority']
        verbose_name = 'AI Контекст'
        verbose_name_plural = 'AI Контексты'

    def __str__(self):
        status = '✓' if self.is_active else '✗'
        return f"[{status}] {self.title}"
