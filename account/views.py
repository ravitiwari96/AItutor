from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404

from .serializers import *
from .models import User    

class StudentSignupView(APIView):
   
    permission_classes = [AllowAny] 
    
    def post(self, request):
        serializer = StudentSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                "message": "Student registered successfully.",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": f"{user.first_name} {user.last_name}".strip(),
                    "user_type": "student"
                },
                "token": token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminSignupView(APIView):
    """
    API endpoint for admin registration
    Required fields: full_name, email, phone_number, admin_code, password, confirm_password
    """
    permission_classes = [AllowAny]  # Allow unauthenticated access
    
    def post(self, request):
        serializer = AdminSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                "message": "Admin registered successfully.",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": f"{user.first_name} {user.last_name}".strip(),
                    "user_type": "admin"
                },
                "token": token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """
    API endpoint for user login (both students and admins)
    Required fields: email, password
    """
    permission_classes = [AllowAny]  # Allow unauthenticated access
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            
            user_type = "student" if user.is_student else "admin" if user.is_admin_user else "user"
            
            return Response({
                "message": "Login successful.",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": f"{user.first_name} {user.last_name}".strip(),
                    "user_type": user_type,
                    "phone": user.phone,
                    "dob": user.dob,
                    "grade_level": user.grade_level if user.is_student else None
                },
                "token": token.key
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(APIView):
    """
    API endpoint to get user profile information
    Requires authentication
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LogoutView(APIView):
    """
    API endpoint for user logout
    Requires authentication
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Delete the user's token to logout
            request.user.auth_token.delete()
            return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)
        except:
            return Response({"error": "Something went wrong."}, status=status.HTTP_400_BAD_REQUEST)

class StudentListView(APIView):
    """
    API endpoint to view all students
    Public access allowed
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        students = User.objects.filter(is_student=True)
        serializer = UserSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AdminListView(APIView):
    """
    API endpoint to view all admins (only for super admins)
    Requires admin authentication
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_admin_user and not request.user.is_superuser:
            return Response({"error": "Access denied. Admin privileges required."}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        admins = User.objects.filter(is_admin_user=True)
        serializer = UserSerializer(admins, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# CRUD Views for Students
class StudentDetailView(APIView):
    """
    Retrieve, update or delete a student instance.
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        return get_object_or_404(User, pk=pk, is_student=True)
    
    def get(self, request, pk):
        """Get student details"""
        # Students can view their own profile, admins can view any student
        if not request.user.is_admin_user and request.user.id != int(pk):
            return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)
        
        student = self.get_object(pk)
        serializer = UserSerializer(student)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, pk):
        """Update student details"""
        # Students can update their own profile, admins can update any student
        if not request.user.is_admin_user and request.user.id != int(pk):
            return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)
        
        student = self.get_object(pk)
        serializer = StudentUpdateSerializer(student, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Student updated successfully.",
                "student": UserSerializer(student).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """Delete student account"""
        # Only admins can delete student accounts
        if not request.user.is_admin_user:
            return Response({"error": "Access denied. Admin privileges required."}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        student = self.get_object(pk)
        student_email = student.email
        student.delete()
        return Response({
            "message": f"Student account {student_email} deleted successfully."
        }, status=status.HTTP_200_OK)

class AdminDetailView(APIView):
    """
    Retrieve, update or delete an admin instance.
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        return get_object_or_404(User, pk=pk, is_admin_user=True)
    
    def get(self, request, pk):
        """Get admin details"""
        # Admins can view their own profile or other admin profiles
        if not request.user.is_admin_user:
            return Response({"error": "Access denied. Admin privileges required."}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        admin = self.get_object(pk)
        serializer = UserSerializer(admin)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, pk):
        """Update admin details"""
        # Admins can update their own profile
        if request.user.id != int(pk) and not request.user.is_superuser:
            return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)
        
        admin = self.get_object(pk)
        serializer = AdminUpdateSerializer(admin, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Admin updated successfully.",
                "admin": UserSerializer(admin).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """Delete admin account"""
        # Only superuser can delete admin accounts
        if not request.user.is_superuser:
            return Response({"error": "Access denied. Superuser privileges required."}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        admin = self.get_object(pk)
        admin_email = admin.email
        admin.delete()
        return Response({
            "message": f"Admin account {admin_email} deleted successfully."
        }, status=status.HTTP_200_OK)

class ChangePasswordView(APIView):
    """
    Change user password
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Delete old token and create new one
            Token.objects.filter(user=user).delete()
            token = Token.objects.create(user=user)
            
            return Response({
                "message": "Password changed successfully.",
                "token": token.key
            }, status=status.HTTP_200_OK)   
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StudentCreateView(APIView):
    """
    Create a new student (for admins)
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if not request.user.is_admin_user:
            return Response({"error": "Access denied. Admin privileges required."}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        serializer = StudentSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Student created successfully.",
                "student": UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminCreateView(APIView):
    """
    Create a new admin (for superusers)
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if not request.user.is_superuser:
            return Response({"error": "Access denied. Superuser privileges required."}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        serializer = AdminSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Admin created successfully.",
                "admin": UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)      