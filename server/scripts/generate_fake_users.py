# scripts/generate_fake_users.py
import os
import django
from faker import Faker
import random

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings') # ← 替换 myproject
django.setup()

from users.models import User, Role  # ← 替换 myapp 为你的实际 app 名
fake = Faker('zh_CN')  # 中文数据

# 可选：先创建几个角色（如果 Role 表为空）


def create_sample_roles():
    role_names = ['管理员', '编辑', '审核员', '访客', '财务', '人事']
    roles = []
    for name in role_names:
        role, created = Role.objects.get_or_create(name=name)
        roles.append(role)
    return roles


def create_fake_users(num=100):
    roles = list(Role.objects.all())
    if not roles:
        roles = create_sample_roles()

    for i in range(num):
        username = fake.user_name() + str(random.randint(10, 99))
        email = fake.email()
        phone = "1" + str(random.randint(3000000000, 9999999999))  # 11位手机号
        department = random.choice(['技术部', '产品部', '运营部', '市场部', '人事部', '财务部'])
        position = random.choice(['工程师', '产品经理', '运营专员', '设计师', 'HR', '会计'])
        status = random.choice([True, True, True, False])  # 75% 启用
        importance = random.randint(1, 5)

        # 创建用户
        user = User.objects.create_user(
            username=username,
            email=email,
            password='123456',  # 所有假用户密码统一
            phone=phone,
            department=department,
            position=position,
            status=status,
            importance=importance,
        )

        # 随机分配 0~3 个角色
        assigned_roles = random.sample(roles, k=random.randint(0, min(3, len(roles))))
        user.roles.set(assigned_roles)

        print(f"✅ 创建用户: {user.username} | 部门: {department} | 角色: {[r.name for r in assigned_roles]}")


if __name__ == '__main__':
    print("🚀 开始生成假用户数据...")
    create_fake_users(100)  # 生成 100 个假用户
    print("🎉 完成！")
