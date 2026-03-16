from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from news.views import NewsViewSet, NewsImageViewSet
from core.views import CompanyInfoViewSet, CertificateViewSet, PartnerViewSet, ContactInfoViewSet, SocialLinkViewSet
from projects.views import ProjectViewSet, ProjectContactViewSet, ProjectCommentViewSet


# Публичный роутер (только для чтения)
public_router = DefaultRouter()
public_router.register(r'company-info', CompanyInfoViewSet)
public_router.register(r'certificates', CertificateViewSet)
public_router.register(r'partners', PartnerViewSet)
public_router.register(r'news', NewsViewSet)
public_router.register(r'news-images', NewsImageViewSet, basename='newsimage')
public_router.register(r'projects', ProjectViewSet)
public_router.register(r'project-contacts', ProjectContactViewSet)
public_router.register(r'project-comments', ProjectCommentViewSet)


contact_info = ContactInfoViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
    'put': 'update',
})

social_links = SocialLinkViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
    'put': 'update',
})

# URL конфигурация
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(public_router.urls)),  # Публичное API
    path('api/admin/', include('user.urls')),  # Админское API
    path('api/contact-info/', contact_info, name='contact-info'),
    path('api/social-links/', social_links, name='social-links'),

]

# Добавляем media файлы для разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
