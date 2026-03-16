from django.contrib import admin
from .models import Project, ProjectContact, ProjectComment

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_current', 'has_image']
    list_filter = ['is_current']

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'is_current', 'image')
        }),
    )

    def has_image(self, obj):
        return bool(obj.image)
    has_image.boolean = True
    has_image.short_description = 'Есть изображение'

@admin.register(ProjectContact)
class ProjectContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'email', 'phone']
    readonly_fields = ['created_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Контактная информация', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Сообщение', {
            'fields': ('message',)
        }),
        ('Системная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(ProjectComment)
class ProjectCommentAdmin(admin.ModelAdmin):
    list_display = ['name_project', 'short_comment', 'created_at']
    list_filter = ['created_at', 'name_project']
    search_fields = ['name_project', 'comment']
    readonly_fields = ['created_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Информация о комментарии', {
            'fields': ('name_project', 'comment')
        }),
        ('Системная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def short_comment(self, obj):
        """Показывает сокращенный комментарий в списке"""
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
    short_comment.short_description = 'Комментарий'