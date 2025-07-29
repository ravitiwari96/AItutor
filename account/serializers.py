from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password
from django.conf import settings
from django.contrib.auth import authenticate

class StudentSignupSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(max_length=255, write_only=True)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=15)
    date_of_birth = serializers.DateField()
    grade_level = serializers.CharField(max_length=50)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User    
        fields = ['full_name', 'email', 'phone_number', 'date_of_birth', 'grade_level', 'password', 'confirm_password']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        
        # Check if email already exists
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists."})
        
        return attrs

    def create(self, validated_data):
        full_name = validated_data.pop('full_name')
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        
        # Split full name into first and last name
        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        user = User.objects.create_user(
            username=validated_data['email'],  # Use email as username
            email=validated_data['email'],
            first_name=first_name,
            last_name=last_name,
            phone=validated_data['phone_number'],
            dob=validated_data['date_of_birth'],
            grade_level=validated_data['grade_level'],
            is_student=True,
            password=password
        )

        return user

class AdminSignupSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(max_length=255, write_only=True)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=15)
    admin_code = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone_number', 'admin_code', 'password', 'confirm_password']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        
        # Check admin code
        if attrs['admin_code'] != settings.ADMIN_CODE:
            raise serializers.ValidationError({"admin_code": "Invalid admin code."})
        
        # Check if email already exists
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists."})
        
        return attrs

    def create(self, validated_data):
        full_name = validated_data.pop('full_name')
        validated_data.pop('confirm_password')
        validated_data.pop('admin_code')
        password = validated_data.pop('password')
        
        # Split full name into first and last name
        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        user = User.objects.create_user(
            username=validated_data['email'],  # Use email as username
            email=validated_data['email'],
            first_name=first_name,
            last_name=last_name,
            phone=validated_data['phone_number'],
            is_admin_user=True,
            is_staff=True,  # Allow admin panel access
            password=password
        )
        
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password.')

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    user_type = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'phone', 'dob', 'grade_level', 'user_type', 'is_student', 'is_admin_user']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
    
    def get_user_type(self, obj):
        if obj.is_student:
            return 'student'
        elif obj.is_admin_user:
            return 'admin'
        return 'user'