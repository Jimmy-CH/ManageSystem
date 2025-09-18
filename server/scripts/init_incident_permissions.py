import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from users.models import CustomPermission, Role


def create_incident_permissions():
    perms = [
        ("view_incident", "查看事件"),
        ("add_incident", "创建事件"),
        ("change_incident", "修改事件"),
        ("delete_incident", "删除事件"),
        ("respond_incident", "响应事件"),
        ("resolve_incident", "解决事件"),
        ("export_incident", "导出事件"),
        ("view_statistics", "查看统计"),
    ]

    for code, name in perms:
        obj, created = CustomPermission.objects.get_or_create(
            codename=code,
            defaults={"name": name, "category": "故障事件管理"}
        )
        if created:
            print(f"✅ 创建权限: {name}")

    # 绑定到“故障管理员”角色
    role, _ = Role.objects.get_or_create(name="故障管理员", defaults={"description": "负责故障事件处理"})
    for code, _ in perms:
        perm = CustomPermission.objects.get(codename=code)
        role.permissions.add(perm)

    print("✅ 权限已绑定到角色「故障管理员」")


if __name__ == "__main__":

    create_incident_permissions()
