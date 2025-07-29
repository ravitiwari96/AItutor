from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_student', 'is_admin_user', 'is_staff', 'is_active')
    
    # Fields that can be used to filter the list
    list_filter = ('is_student', 'is_admin_user', 'is_staff', 'is_active', 'date_joined')
    
    # Fields that can be searched
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    
    # Read-only fields
    readonly_fields = ('date_joined', 'last_login')
    
    # Ordering
    ordering = ('email',)
    
    # Fieldsets for the user edit form
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('is_student', 'is_admin_user', 'phone', 'dob', 'grade_level')
        }),
    )
    
    # Fields to show when adding a new user
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('is_student', 'is_admin_user', 'phone', 'dob', 'grade_level')
        }),
    )

# Register your models here.
admin.site.register(User, CustomUserAdmin)