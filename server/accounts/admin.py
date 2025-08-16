from django.contrib import admin
from accounts.models import UserRole, Role, CustomPermission

admin.site.register(UserRole)
admin.site.register(Role)
admin.site.register(CustomPermission)
