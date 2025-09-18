from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()

# ⚠️ 强制取消默认注册（如果之前被注册过）
if admin.site.is_registered(User):
    admin.site.unregister(User)

# ✅ 重新注册
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = [
        'username',
        'phone',
        'department',
        'position',
        'status',
        'is_staff',
        'is_superuser',
        'is_active'
    ]
    list_filter = ['status', 'is_staff', 'is_superuser', 'is_active', 'department']
    search_fields = ['username', 'phone', 'department', 'position']
    ordering = ['-id']

    fieldsets = UserAdmin.fieldsets + (
        ('扩展信息', {
            'fields': ('phone', 'avatar', 'department', 'position', 'status', 'importance')
        }),
        ('角色权限', {
            'fields': ('roles',),
            'classes': ('collapse',)
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('扩展信息', {
            'classes': ('wide',),
            'fields': ('phone', 'department', 'position', 'status', 'importance'),
        }),
    )