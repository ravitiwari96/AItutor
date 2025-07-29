from django.urls import path
from .views import (
    StudentSignupView, 
    AdminSignupView, 
    LoginView, 
    ProfileView, 
    LogoutView,
    StudentListView,
    AdminListView
)

urlpatterns = [
    # Authentication URLs
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Registration URLs
    path('signup/student/', StudentSignupView.as_view(), name='student-signup'),
    path('signup/admin/', AdminSignupView.as_view(), name='admin-signup'),
    
    # Profile URLs
    path('profile/', ProfileView.as_view(), name='profile'),
    
    # Admin URLs
    path('students/', StudentListView.as_view(), name='student-list'),
    path('admins/', AdminListView.as_view(), name='admin-list'),
]