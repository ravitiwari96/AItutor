# models.py (in account app)
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_student = models.BooleanField(default=False)
    is_admin_user = models.BooleanField(default=False)
    phone = models.CharField(max_length=15, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    grade_level = models.CharField(max_length=50, null=True, blank=True)
    
    # Use email as the username field for login
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        user_type = "Student" if self.is_student else "Admin" if self.is_admin_user else "User"
        return f"{self.email} ({user_type})"