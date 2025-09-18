
import os
import django
from django.db import transaction

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings') # ← 替换 myproject
django.setup()

from users.models import CustomPermission, Role, User  # 👈 替换 your_app


def clear_permissions():
    count = CustomPermission.objects.all().count()
    CustomPermission.objects.all().delete()
    print(f"🗑️  已删除 {count} 个自定义权限")


def clear_roles():
    count = Role.objects.all().count()
    Role.objects.all().delete()
    print(f"🗑️  已删除 {count} 个角色")


def clear_users(keep_superusers=True):
    qs = User.objects.all()
    if keep_superusers:
        qs = qs.filter(is_superuser=False)
    count = qs.count()
    qs.delete()
    if keep_superusers:
        print(f"🗑️  已删除 {count} 个普通用户（保留超级用户）")
    else:
        print(f"🗑️  已删除 {count} 个用户（包括超级用户）")


@transaction.atomic
def main(clear_perms=True, clear_roles_flag=True, clear_users_flag=True, keep_superusers=True):
    print("⚠️  准备清空数据，请确认操作...")
    if clear_perms:
        clear_permissions()
    if clear_roles_flag:
        clear_roles()
    if clear_users_flag:
        clear_users(keep_superusers=keep_superusers)
    print("✅ 数据清空完成！")


if __name__ == "__main__":
    # ========== 自定义清空范围 ==========
    main(
        clear_perms=True,        # 是否清空权限
        clear_roles_flag=True,   # 是否清空角色
        clear_users_flag=True,   # 是否清空用户
        keep_superusers=True     # 是否保留超级用户（强烈建议保留）
    )