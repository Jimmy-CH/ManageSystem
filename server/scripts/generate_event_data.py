# scripts/generate_incident_data.py

import os
import random
import django
from faker import Faker
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from events.models import (
    Category, SLAStandard, Incident, Fault
)
from users.models import (
    User, CustomPermission, Role
)


fake = Faker('zh_CN')


def create_categories():
    """
    创建分类树：
    硬件故障
      ├─ 服务器
      │   ├─ CPU
      │   ├─ 内存
      │   └─ 硬盘
      └─ 网络设备
          ├─ 路由器
          └─ 交换机
    软件故障
      ├─ 数据库
      ├─ 中间件
      └─ 应用服务
    """
    root1 = Category.objects.get_or_create(name="硬件故障", level=1, order=1)[0]
    root2 = Category.objects.get_or_create(name="软件故障", level=1, order=2)[0]

    server = Category.objects.get_or_create(name="服务器", parent=root1, level=2, order=1)[0]
    network = Category.objects.get_or_create(name="网络设备", parent=root1, level=2, order=2)[0]

    Category.objects.get_or_create(name="CPU", parent=server, level=3, order=1)
    Category.objects.get_or_create(name="内存", parent=server, level=3, order=2)
    Category.objects.get_or_create(name="硬盘", parent=server, level=3, order=3)

    Category.objects.get_or_create(name="路由器", parent=network, level=3, order=1)
    Category.objects.get_or_create(name="交换机", parent=network, level=3, order=2)

    db = Category.objects.get_or_create(name="数据库", parent=root2, level=2, order=1)[0]
    middleware = Category.objects.get_or_create(name="中间件", parent=root2, level=2, order=2)[0]
    app = Category.objects.get_or_create(name="应用服务", parent=root2, level=2, order=3)[0]

    Category.objects.get_or_create(name="MySQL", parent=db, level=3, order=1)
    Category.objects.get_or_create(name="Redis", parent=db, level=3, order=2)
    Category.objects.get_or_create(name="Nginx", parent=middleware, level=3, order=1)
    Category.objects.get_or_create(name="订单服务", parent=app, level=3, order=1)
    Category.objects.get_or_create(name="支付服务", parent=app, level=3, order=2)

    print("✅ 分类树创建完成")


def create_sla_standards():
    data = [
        {"level_name": "P1", "priority": 4, "response_time": 0.5, "resolve_time": 2, "description": "重大故障，全站不可用"},
        {"level_name": "P2", "priority": 3, "response_time": 1, "resolve_time": 4, "description": "核心功能不可用"},
        {"level_name": "P3", "priority": 2, "response_time": 4, "resolve_time": 24, "description": "非核心功能异常"},
        {"level_name": "P4", "priority": 1, "response_time": 24, "resolve_time": 72, "description": "轻微问题或咨询"},
    ]
    for item in data:
        SLAStandard.objects.get_or_create(
            priority=item["priority"],
            defaults={
                "level_name": item["level_name"],
                "response_time": item["response_time"],
                "resolve_time": item["resolve_time"],
                "description": item["description"]
            }
        )
    print("✅ SLA标准创建完成")


def create_incidents_and_faults(num_incidents=50):
    # 获取用户（用于 reporter 和 assignee）
    users = list(User.objects.all()[:10])  # 最多取前10个用户
    if len(users) < 2:
        print("⚠️  用户不足，请先运行 fake_data 脚本生成用户")
        return

    # 获取分类（排除根节点，只取叶子或具体分类）
    categories = list(Category.objects.filter(level=3))  # 只取第3级分类
    slas = list(SLAStandard.objects.all())

    for i in range(num_incidents):
        priority = random.randint(1, 4)
        sla = next((s for s in slas if s.priority == priority), None)

        occurred_at = fake.date_time_between(start_date='-30d', end_date='now', tzinfo=timezone.get_current_timezone())

        incident = Incident.objects.create(
            title=fake.sentence(nb_words=6)[:-1] + "故障",
            description=fake.text(max_nb_chars=200),
            category=random.choice(categories) if categories else None,
            priority=priority,
            source=random.choice([1, 2, 3, 4]),
            reporter=random.choice(users),
            assignee=random.choice(users),
            status=random.choice([0, 1, 2]),
            occurred_at=occurred_at,
            responded_at=occurred_at + timedelta(minutes=random.randint(10, 120)) if random.random() > 0.3 else None,
            resolved_at=occurred_at + timedelta(hours=random.randint(1, 48)) if random.random() > 0.5 else None,
            sla=sla,
            is_active=True
        )

        # 创建1~2个故障记录（一个事件可能包含多个故障点）
        for j in range(random.randint(1, 2)):
            Fault.objects.create(
                incident=incident,
                detail=fake.text(max_nb_chars=150),
                root_cause=fake.sentence() if random.random() > 0.3 else None,
                solution=fake.sentence() if random.random() > 0.2 else None,
                downtime_minutes=random.randint(5, 120),
                impact_scope=random.choice(["单用户", "部分用户", "区域用户", "全部用户"]),
                status=incident.status
            )

    print(f"✅ 创建了 {num_incidents} 个事件和 {Incident.objects.count()*1.5:.0f} 个故障记录")


def main():
    print("🚀 开始生成故障事件系统假数据...")
    create_categories()
    create_sla_standards()
    create_incidents_and_faults(50)
    print("🎉 故障事件系统假数据生成完成！")


if __name__ == "__main__":
    main()
