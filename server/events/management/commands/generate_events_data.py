
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from faker import Faker
import random

# 安全防护：仅 DEBUG 模式运行
if not settings.DEBUG:
    raise RuntimeError("❌ 禁止在生产环境运行此命令！")

# 导入你的模型（根据实际路径调整）
from events.models import Category, SLAStandard, Incident, Fault
from events.constants import PRIORITY_CHOICES, SOURCE_CHOICES, FAULT_STATUS_CHOICES

User = get_user_model()
fake = Faker('zh_CN')


class Command(BaseCommand):
    help = '生成事件、故障、分类、SLA 和用户测试数据'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=10, help='生成用户数')
        parser.add_argument('--categories', type=int, default=15, help='生成分类数（含子分类）')
        parser.add_argument('--incidents', type=int, default=30, help='生成事件数')
        parser.add_argument('--faults', type=int, default=20, help='生成故障数')
        parser.add_argument('--clear', action='store_true', help='清空现有数据（保留 admin）')

    def handle(self, *args, **options):
        users_n = options['users']
        cats_n = options['categories']
        incs_n = options['incidents']
        faults_n = options['faults']
        clear = options['clear']

        if clear:
            self.stdout.write(self.style.WARNING("⚠️ 正在清空测试数据..."))
            Fault.objects.all().delete()
            Incident.objects.all().delete()
            SLAStandard.objects.all().delete()
            Category.objects.all().delete()
            User.objects.exclude(username='admin').delete()

        # ========================
        # 1. 创建用户
        # ========================
        users = []
        for _ in range(users_n):
            try:
                user = User.objects.create_user(
                    username=fake.unique.user_name(),
                    email=fake.unique.email(),
                    password='123456',
                    phone=fake.phone_number()[:11],
                    department=fake.company()[:50],
                    position=fake.job()[:50],
                    status=True,
                    importance=random.randint(1, 5),
                )
                users.append(user)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠️ 用户创建失败: {e}"))
        self.stdout.write(self.style.SUCCESS(f"✅ 用户: {len(users)} 个"))

        # ========================
        # 2. 创建 SLA 标准 (P1-P4)
        # ========================
        sla_levels = [
            {"name": "P1", "priority": 1, "response": 1, "resolve": 4},
            {"name": "P2", "priority": 2, "response": 2, "resolve": 8},
            {"name": "P3", "priority": 3, "response": 4, "resolve": 24},
            {"name": "P4", "priority": 4, "response": 8, "resolve": 72},
        ]
        slas = []
        for lvl in sla_levels:
            sla, created = SLAStandard.objects.get_or_create(
                priority=lvl["priority"],
                defaults={
                    "level_name": lvl["name"],
                    "response_time": lvl["response"],
                    "resolve_time": lvl["resolve"],
                    "description": f"{lvl['name']} 级别事件处理标准"
                }
            )
            slas.append(sla)
        self.stdout.write(self.style.SUCCESS(f"✅ SLA 标准: {len(slas)} 个"))

        # ========================
        # 3. 创建分类树（支持多级）
        # ========================
        categories = []
        # 先创建根分类
        root_cats = []
        for i in range(3):
            cat = Category.objects.create(
                name=fake.word().capitalize() + "类",
                parent=None,
                level=1,
                order=i,
                is_active=True
            )
            categories.append(cat)
            root_cats.append(cat)

        # 再创建子分类
        remaining = cats_n - len(root_cats)
        for _ in range(remaining):
            parent = random.choice(root_cats)
            cat = Category.objects.create(
                name=fake.word().capitalize() + "子类",
                parent=parent,
                level=2,
                order=random.randint(1, 10),
                is_active=True
            )
            categories.append(cat)
        self.stdout.write(self.style.SUCCESS(f"✅ 分类: {len(categories)} 个"))

        # ========================
        # 4. 创建事件 (Incident)
        # ========================
        incidents = []
        for _ in range(incs_n):
            reporter = random.choice(users) if users else None
            assignee = random.choice(users) if users else None
            category = random.choice(categories) if categories else None
            priority = random.choice([p[0] for p in PRIORITY_CHOICES])
            sla = SLAStandard.objects.filter(priority=priority).first()

            incident = Incident.objects.create(
                title=fake.sentence(nb_words=4)[:200],
                description=fake.text(max_nb_chars=500),
                category=category,
                priority=priority,
                source=random.choice([s[0] for s in SOURCE_CHOICES]),
                reporter=reporter,
                assignee=assignee,
                status=random.choice([s[0] for s in FAULT_STATUS_CHOICES]),
                occurred_at=fake.date_time_between(start_date="-30d", tzinfo=timezone.get_current_timezone()),
                sla=sla,
                is_active=True
            )
            incidents.append(incident)
        self.stdout.write(self.style.SUCCESS(f"✅ 事件: {len(incidents)} 个"))

        # ========================
        # 5. 创建故障 (Fault)
        # ========================
        created_faults = 0
        for _ in range(faults_n):
            if not incidents:
                break
            incident = random.choice(incidents)
            # 避免重复创建（一个事件可有多个故障，但这里简单处理）
            fault = Fault.objects.create(
                incident=incident,
                detail=fake.text(max_nb_chars=300),
                root_cause=fake.text(max_nb_chars=200),
                solution=fake.text(max_nb_chars=300),
                downtime_minutes=random.randint(0, 1440),  # 0~24小时
                impact_scope=fake.sentence(nb_words=3)[:200],
                status=random.choice([s[0] for s in FAULT_STATUS_CHOICES])
            )
            created_faults += 1
        self.stdout.write(self.style.SUCCESS(f"✅ 故障: {created_faults} 个"))

        self.stdout.write(self.style.SUCCESS("🎉 事件系统测试数据填充完成！"))
