from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Создаем роутер для админских ViewSet'ов
admin_router = DefaultRouter()
admin_router.register(r'news', views.AdminNewsViewSet, basename='admin-news')
admin_router.register(r'projects', views.AdminProjectViewSet, basename='admin-projects')
admin_router.register(r'project-contacts', views.AdminProjectContactViewSet, basename='admin-project-contacts')
admin_router.register(r'project-comments', views.AdminProjectCommentViewSet, basename='admin-project-comments')
admin_router.register(r'company-info', views.AdminCompanyInfoViewSet, basename='admin-company-info')
admin_router.register(r'certificates', views.AdminCertificateViewSet, basename='admin-certificates')
admin_router.register(r'partners', views.AdminPartnerViewSet, basename='admin-partners')

urlpatterns = [
    # Регистрация и авторизация
    path('register/', views.admin_register, name='admin-register'),
    path('login/', views.admin_login, name='admin-login'),
    path('logout/', views.admin_logout, name='admin-logout'),

    # Админские API
    path('', include(admin_router.urls)),
]