
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from faker import Faker
import random

# 安全防护：仅允许在 DEBUG 模式下运行
if not settings.DEBUG:
    raise RuntimeError("❌ 禁止在生产环境运行此数据生成命令！")

# 导入你的模型（请根据实际 app 名修改 'your_app'）
from users.models import CustomPermission, Role

User = get_user_model()
fake = Faker('zh_CN')


class Command(BaseCommand):
    help = '生成测试用的自定义权限、角色和用户数据（兼容 BaseModel 和时区）'

    def add_arguments(self, parser):
        parser.add_argument('--perms', type=int, default=10, help='生成的权限数量（默认: 10）')
        parser.add_argument('--roles', type=int, default=5, help='生成的角色数量（默认: 5）')
        parser.add_argument('--users', type=int, default=20, help='生成的用户数量（默认: 20）')
        parser.add_argument('--clear', action='store_true', help='清空现有测试数据（保留 admin 用户）')

    def handle(self, *args, **options):
        perms_count = options['perms']
        roles_count = options['roles']
        users_count = options['users']
        clear = options['clear']

        if clear:
            self.stdout.write(self.style.WARNING("⚠️ 正在清空权限、角色和非 admin 用户..."))
            User.objects.exclude(username='admin').delete()
            Role.objects.all().delete()
            CustomPermission.objects.all().delete()

        # ========================
        # Step 1: 生成权限
        # ========================
        permissions = []
        categories = ['user', 'content', 'system', 'report', 'audit']
        for i in range(perms_count):
            perm = CustomPermission.objects.create(
                codename=f"{fake.word().lower()}_perm_{i}",
                name=fake.sentence(nb_words=2)[:50],
                description=fake.text(max_nb_chars=100),
                category=random.choice(categories),
                importance=random.randint(1, 5),
                status=True,
                create_user_name="admin",
                change_user_name="admin"
                # create_time / update_time 由 auto_now_add / auto_now 自动处理
            )
            permissions.append(perm)

        self.stdout.write(self.style.SUCCESS(f"✅ 成功生成 {len(permissions)} 个权限"))

        # ========================
        # Step 2: 生成角色
        # ========================
        roles = []
        for i in range(roles_count):
            role = Role.objects.create(
                name=fake.unique.job()[:50],
                description=fake.sentence(nb_words=4)[:200],
                importance=random.randint(1, 5),
                status=True,
                create_user_name="admin",
                change_user_name="admin"
            )
            # 随机分配 1~5 个权限
            k = min(random.randint(1, 5), len(permissions))
            assigned_perms = random.sample(permissions, k=k)
            role.permissions.set(assigned_perms)
            roles.append(role)

        self.stdout.write(self.style.SUCCESS(f"✅ 成功生成 {len(roles)} 个角色"))

        # ========================
        # Step 3: 生成用户
        # ========================
        created_users = 0
        for _ in range(users_count):
            username = fake.unique.user_name()
            email = fake.unique.email()

            try:
                # 使用 create_user 创建用户（仅传支持的字段）
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='123456',
                    phone=fake.phone_number()[:11],
                    department=fake.company()[:50],
                    position=fake.job()[:50],
                    status=True,
                    importance=random.randint(1, 5),
                    # ❌ 不传 BaseModel 中的 create_user_name 等字段！
                )

                # 手动设置 BaseModel 字段（create_time 由 auto_now_add 自动设）
                # user.create_user_name = "admin"
                # user.change_user_name = "admin"
                # user.save(update_fields=['create_user_name', 'change_user_name'])

                # 随机分配角色（2/3 概率）
                if roles and random.choice([True, True, False]):
                    k = min(random.randint(1, 2), len(roles))
                    assigned_roles = random.sample(roles, k=k)
                    user.roles.set(assigned_roles)

                created_users += 1

            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠️ 用户 {username} 创建失败: {e}"))

        self.stdout.write(self.style.SUCCESS(f"✅ 成功生成 {created_users} 个用户"))
        self.stdout.write(self.style.SUCCESS("🎉 测试数据填充完成！"))
