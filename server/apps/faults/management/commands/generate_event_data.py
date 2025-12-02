import random
import string
from decimal import Decimal
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.faults.models import (
    EventCategory,
    EventComponentInfo,
    Event,
    EventDeviceInfo,
    EventHandleProcess,
    EventTimeEffective,
    EventTimeSpecial
)


def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def random_ip():
    return ".".join(str(random.randint(0, 255)) for _ in range(4))


class Command(BaseCommand):
    help = 'Generate sample data for event management models'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=5, help='Number of events to create')

    def handle(self, *args, **options):
        count = options['count']
        self.stdout.write("开始生成事件管理测试数据...")

        # 1. 创建事件分类（EventCategory）
        root_cats = []
        for i in range(3):
            cat = EventCategory.objects.create(
                name=f"一级分类-{i+1}",
                active=1,
                parent=None,
                depth=1
            )
            root_cats.append(cat)

        sub_cats = []
        for parent in root_cats:
            for j in range(2):
                sub = EventCategory.objects.create(
                    name=f"{parent.name}-子类{j+1}",
                    active=1,
                    parent=parent,
                    depth=2
                )
                sub_cats.append(sub)

        all_categories = root_cats + sub_cats
        self.stdout.write(f"✅ 创建 {len(all_categories)} 个事件分类")

        # 2. 创建部件信息（EventComponentInfo）
        components = []
        brands = ["华为", "戴尔", "联想", "HPE", "IBM"]
        models_ = ["Model-X", "ServerPro", "RackMate", "ThinkSystem"]
        for i in range(10):
            comp = EventComponentInfo.objects.create(
                event_sub=random.choice(all_categories),
                component_sn=f"SN-COMP-{random_string(6)}",
                component_name=f"部件-{i+1}",
                component_brand=random.choice(brands),
                component_model=random.choice(models_),
                component_specification=f"Spec-{random.randint(1, 10)}",
                slot=f"Slot-{random.randint(1, 8)}",
                component_info={
                    "warranty": f"{random.randint(1,5)}年",
                    "vendor_code": random_string(10)
                }
            )
            components.append(comp)
        self.stdout.write(f"✅ 创建 {len(components)} 个部件信息")

        # 3. 创建事件（Event）
        events = []
        registrants = ["张三", "李四", "王五", "赵六"]
        handlers = ["运维A", "运维B", "厂商工程师"]
        for i in range(count):
            start_ts = int((timezone.now() - timedelta(days=random.randint(1, 30))).timestamp())
            end_ts = start_ts + random.randint(600, 86400)  # 10分钟 ~ 24小时
            duration = (end_ts - start_ts) // 60  # 转为分钟

            event = Event.objects.create(
                category=random.choice([1, 2, 3]),
                level=random.choice([1, 2, 3, 4]),
                registrant=random.choice(registrants),
                handler=random.choice(handlers),
                mal_id=f"MAL-{datetime.now().strftime('%Y%m%d')}-{str(i+1).zfill(4)}",
                start_time=start_ts,
                end_time=end_ts,
                duration=duration,
                mal_reason="硬件故障" if random.random() > 0.5 else "软件异常",
                cause_department={"dept": random.choice(["网络部", "服务器组", "DBA团队"])},
                solution="更换部件" if random.random() > 0.5 else "重启服务",
                description=f"服务器 {random_ip()} 出现异常，表现为...",
                mal_result=random.choice([1, 2, 3]),
                reason="电源模块老化",
                key_endpoint="核心交换机-端口48",
                maintenance="ABC维保公司",
                maintenance_type=random.choice([1, 2]),
                impact_pro={"projects": ["项目A", "项目B"]},
                maintenance_remarks={"score": random.randint(1, 5), "comment": "响应及时"},
                first_level=random.choice(root_cats).name,
                subdivision=random.choice(sub_cats).name,
                third_level="三级默认",
                fourth_level="四级默认",
                is_overtime=random.choice([0, 1, 2]),
                score=random.randint(0, 100),
                maintenance_duration=random.randint(30, 720),  # 30分钟 ~ 12小时
                maintenance_status=random.choice([0, 1, 2]),
                solution_type=random.choice([0, 1, 2]),
                document_id=f"DOC-{random_string(8)}"
            )
            events.append(event)
        self.stdout.write(f"✅ 创建 {len(events)} 个事件")

        # 4. 创建设备信息（EventDeviceInfo）
        for event in events:
            for j in range(random.randint(1, 3)):  # 每个事件关联1~3台设备
                EventDeviceInfo.objects.create(
                    event=event,
                    equipment_ip=random_ip(),
                    equipment_sn=f"SN-EQ-{random_string(8)}",
                    machine_info=f"Server-Type-{random.choice(['物理机', '虚拟机'])}",
                    rack_location=f"机房{random.randint(1,5)}-机柜{random.randint(1,20)}",
                    brand=random.choice(brands),
                    device_model=random.choice(models_),
                    device_location=f"IDC-{random.choice(['北京', '上海', '深圳'])}",
                    device_name=f"DB-Primary-{j+1}",
                    component_name=f"CPU-{random.randint(1,4)}",
                    component_brand="Intel",
                    component_specification="Xeon Gold 6330",
                    slot=f"CPU{j+1}"
                )
        self.stdout.write(f"✅ 创建设备信息（约 {count * 2} 条）")

        # 5. 创建处理过程（EventHandleProcess）
        steps = [
            "1. 接收告警\n2. 远程登录检查",
            "1. 现场排查\n2. 更换故障硬盘\n3. 验证服务恢复",
            "1. 联系厂商\n2. 升级固件\n3. 监控24小时"
        ]
        for event in events:
            EventHandleProcess.objects.create(
                event=event,
                handle_process=random.choice(steps)
            )
        self.stdout.write(f"✅ 创建 {len(events)} 条处理过程")

        # 6. 创建标准时效（EventTimeEffective）
        for cat in [1, 2]:
            for lvl in [1, 2, 3]:
                EventTimeEffective.objects.get_or_create(
                    category=cat,
                    first_level="默认",
                    second_level="默认二级",
                    third_level="",
                    fourth_level="",
                    level=lvl,
                    standard=Decimal(str(round(random.uniform(30, 720), 2)))
                )
        self.stdout.write("✅ 创建标准时效规则")

        # 7. 创建特殊时效（EventTimeSpecial）
        for comp in random.sample(components, min(5, len(components))):
            EventTimeSpecial.objects.create(
                component_name=comp.component_name,
                component_brand=comp.component_brand,
                component_model=comp.component_model,
                standard=Decimal(str(round(random.uniform(60, 1440), 2)))
            )
        self.stdout.write("✅ 创建特殊时效规则")

        self.stdout.write(
            self.style.SUCCESS(f'🎉 成功生成 {count} 个完整事件及其关联数据！')
        )


