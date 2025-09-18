
import os
import random
import django
from faker import Faker

# 设置 Django 环境（根据你的项目结构调整）
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings') # ← 替换 myproject
django.setup()

from users.models import CustomPermission, Role, User  # 👈 替换 your_app 为你的实际 app 名
from django.contrib.auth.hashers import make_password

fake = Faker('zh_CN')  # 使用中文数据

# 清空旧数据（可选，谨慎使用）
# CustomPermission.objects.all().delete()
# Role.objects.all().delete()
# User.objects.filter(is_superuser=False).delete()  # 保留超级用户


def create_permissions():
    permissions_data = [
        {"codename": "can_publish", "name": "发布内容", "category": "content", "importance": 2},
        {"codename": "can_edit", "name": "编辑内容", "category": "content", "importance": 2},
        {"codename": "can_delete", "name": "删除内容", "category": "content", "importance": 3},
        {"codename": "can_manage_user", "name": "管理用户", "category": "user", "importance": 4},
        {"codename": "can_view_log", "name": "查看日志", "category": "system", "importance": 1},
        {"codename": "can_backup_db", "name": "备份数据库", "category": "system", "importance": 5},
        {"codename": "can_assign_role", "name": "分配角色", "category": "user", "importance": 4},
        {"codename": "can_export_data", "name": "导出数据", "category": "content", "importance": 3},
    ]

    permissions = []
    for data in permissions_data:
        perm, created = CustomPermission.objects.get_or_create(
            codename=data["codename"],
            defaults={
                "name": data["name"],
                "description": f"权限描述：{data['name']}",
                "category": data["category"],
                "importance": data["importance"],
                "status": True
            }
        )
        permissions.append(perm)
    print(f"✅ 创建/获取了 {len(permissions)} 个权限")
    return permissions


def create_roles(permissions):
    roles_data = [
        {"name": "内容编辑", "description": "负责内容编辑与发布", "importance": 2},
        {"name": "管理员", "description": "系统管理员", "importance": 5},
        {"name": "审核员", "description": "内容审核人员", "importance": 3},
        {"name": "访客", "description": "只读权限用户", "importance": 1},
    ]

    roles = []
    for data in roles_data:
        role, created = Role.objects.get_or_create(
            name=data["name"],
            defaults={
                "description": data["description"],
                "importance": data["importance"],
                "status": True
            }
        )
        roles.append(role)

        # 为角色分配权限（随机分配部分权限）
        if role.name == "内容编辑":
            role.permissions.set([p for p in permissions if p.category == "content"])
        elif role.name == "管理员":
            role.permissions.set(permissions)  # 所有权限
        elif role.name == "审核员":
            role.permissions.set([p for p in permissions if p.codename in ["can_view_log", "can_edit"]])
        elif role.name == "访客":
            role.permissions.set([p for p in permissions if p.importance <= 2])

    print(f"✅ 创建/获取了 {len(roles)} 个角色")
    return roles


def create_users(roles, num_users=20):
    users = []

    for i in range(num_users):
        username = fake.user_name() + str(random.randint(100, 999))
        email = fake.email()
        phone = fake.phone_number()[:11]
        department = random.choice(["技术部", "产品部", "运营部", "市场部", "人事部"])
        position = random.choice(["工程师", "产品经理", "运营专员", "设计师", "HR"])

        # 随机分配 1~2 个角色
        assigned_roles = random.sample(roles, k=random.randint(1, min(2, len(roles))))

        user = User.objects.create(
            username=username,
            email=email,
            phone=phone,
            department=department,
            position=position,
            status=True,
            importance=random.randint(1, 5),
            password=make_password("123456")  # 默认密码 123456
        )
        user.roles.set(assigned_roles)
        users.append(user)

    print(f"✅ 创建了 {len(users)} 个用户")
    return users


def main():
    print("🚀 开始生成假数据...")
    permissions = create_permissions()
    roles = create_roles(permissions)
    create_users(roles, num_users=100)
    print("🎉 假数据生成完成！")


if __name__ == "__main__":
    main()
