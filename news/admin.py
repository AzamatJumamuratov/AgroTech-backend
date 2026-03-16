from django.contrib import admin
from .models import News

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'published_at', 'is_announcement']
    list_filter = ['is_announcement', 'published_at']
    ordering = ['-published_at']

    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'is_announcement')
        }),
    )