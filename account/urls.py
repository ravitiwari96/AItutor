from django.urls import path

from .views import (
    StudentSignupView, 
    AdminSignupView, 
    LoginView, 
    ProfileView, 
    LogoutView,
    StudentListView,
    AdminListView,
    StudentDetailView,
    AdminDetailView,
    ChangePasswordView,
    StudentCreateView,
    AdminCreateView
)

urlpatterns = [
    # Authentication URLs
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Registration URLs (public)
    path('signup/student/', StudentSignupView.as_view(), name='student-signup'),
    path('signup/admin/', AdminSignupView.as_view(), name='admin-signup'),
    
    # Profile URLs
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # Student CRUD URLs
    path('students/', StudentListView.as_view(), name='student-list'),
    path('students/create/', StudentCreateView.as_view(), name='student-create'),
    path('students/<int:pk>/', StudentDetailView.as_view(), name='student-detail'),
    
    # Admin CRUD URLs
    path('admins/', AdminListView.as_view(), name='admin-list'),
    path('admins/create/', AdminCreateView.as_view(), name='admin-create'),
    path('admins/<int:pk>/', AdminDetailView.as_view(), name='admin-detail'),
]