from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from .serializers import StudentSignupSerializer, AdminSignupSerializer, LoginSerializer, UserSerializer
from .models import User

class StudentSignupView(APIView):
    """
    API endpoint for student registration
    Required fields: full_name, email, phone_number, date_of_birth, grade_level, password, confirm_password
    """
    permission_classes = [AllowAny]  # Allow unauthenticated access
    
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
    API endpoint for admins to view all students
    Requires admin authentication
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_admin_user:
            return Response({"error": "Access denied. Admin privileges required."}, 
                          status=status.HTTP_403_FORBIDDEN)
        
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