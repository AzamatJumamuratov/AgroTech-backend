from django.db import models
from django.contrib.auth.models import User


class ChatSession(models.Model):
    """Сессия чата пользователя."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=255, blank=True, help_text='Авто-генерируется из первого сообщения')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Чат-сессия'
        verbose_name_plural = 'Чат-сессии'

    def __str__(self):
        return f"Чат #{self.pk} — {self.user.username}: {self.title[:50]}"


class ChatMessage(models.Model):
    """Сообщение в чате."""
    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('assistant', 'Ассистент'),
    ]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()

    # Метаданные: pdf_url, sources, action_type, related_projects и т.д.
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Сообщение чата'
        verbose_name_plural = 'Сообщения чатов'

    def __str__(self):
        return f"[{self.role}] {self.content[:50]}"
