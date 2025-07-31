from django.urls import path
from . import views

urlpatterns = [
    # AI Chat Endpoints
    path('chat/', views.chat_with_ai, name='chat_with_ai'),
    path('chat/list/', views.list_user_chats, name='list_user_chats'),
    
    # Educational AI Endpoints
    path('explain/', views.explain_concept, name='explain_concept'),
    path('content/generate/', views.generate_educational_content, name='generate_educational_content'),
    
    # System Status
    path('status/', views.api_status, name='api_status'),
    path('service/status/', views.service_status, name='service_status'),
]
