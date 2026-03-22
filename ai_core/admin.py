from django.contrib import admin
from .models import DocumentEmbedding, AIContext


@admin.register(AIContext)
class AIContextAdmin(admin.ModelAdmin):
    list_display = ['key', 'title', 'is_active', 'priority', 'updated_at']
    list_filter = ['is_active']
    search_fields = ['key', 'title', 'content']
    list_editable = ['is_active', 'priority']


@admin.register(DocumentEmbedding)
class DocumentEmbeddingAdmin(admin.ModelAdmin):
    list_display = ['source_type', 'source_id', 'language', 'content_title', 'updated_at']
    list_filter = ['source_type', 'language']
    search_fields = ['content_title', 'content_text']
    readonly_fields = ['embedding']
