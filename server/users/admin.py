
from django.contrib import admin
from .models import CustomPermission, User
from django.contrib.auth.admin import UserAdmin


@admin.register(CustomPermission)
class CustomPermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'codename', 'category')
    list_filter = ('category',)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # 继承默认 UserAdmin，保留所有功能
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    fieldsets = UserAdmin.fieldsets
