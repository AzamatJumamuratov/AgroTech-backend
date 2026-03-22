from django.urls import path
from . import views

urlpatterns = [
    path('sessions/', views.sessions_list, name='chat-sessions'),
    path('sessions/<int:session_id>/', views.session_detail, name='chat-session-detail'),
    path('sessions/<int:session_id>/messages/', views.send_message, name='chat-send-message'),
]
