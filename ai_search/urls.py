from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search_news_view, name='ai-search-news'),
    path('search/all/', views.search_all_view, name='ai-search-all'),
]
