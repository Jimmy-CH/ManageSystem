
import random
from datetime import timedelta, date
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from idc.models import DataCenter, Rack, Device, IPAddress, WorkOrder

User = get_user_model()


class Command(BaseCommand):
    help = "生成 IDC 测试数据"

    def handle(self, *args, **options):
        self.stdout.write("开始生成测试数据...")

        # 1. 创建用户（如果不存在）
        admin_user, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "is_staff": True,
                "is_superuser": True
            }
        )
        if not admin_user.password:
            admin_user.set_password("admin123")
            admin_user.save()

        users = []
        for i in range(1, 6):
            user, _ = User.objects.get_or_create(
                username=f"user{i}",
                defaults={"email": f"user{i}@example.com"}
            )
            if not user.password:
                user.set_password("user123")
                user.save()
            users.append(user)

        # 2. 创建机房
        data_centers = []
        levels = ['A', 'B', 'C']
        for i in range(1, 4):
            dc, created = DataCenter.objects.get_or_create(
                name=f"北京数据中心-{i}",
                defaults={
                    "address": f"北京市朝阳区XX路{i}号",
                    "contact": f"联系人{i}",
                    "phone": f"1380013800{i}",
                    "level": random.choice(levels),
                    "is_active": True
                }
            )
            if created:
                self.stdout.write(f"✅ 创建机房: {dc.name}")
            data_centers.append(dc)

        # 3. 创建机柜
        racks = []
        for dc in data_centers:
            for j in range(1, 6):  # 每个机房5个机柜
                rack, created = Rack.objects.get_or_create(
                    data_center=dc,
                    name=f"RACK-{j:02d}",
                    defaults={
                        "height": 42,
                        "power_load": round(random.uniform(3.0, 10.0), 1),
                        "location": f"第{j}排第{chr(64 + j)}列"
                    }
                )
                if created:
                    self.stdout.write(f"✅ 创建机柜: {rack}")
                racks.append(rack)

        # 4. 创建设备
        device_types = [t[0] for t in Device.DEVICE_TYPES]
        statuses = [s[0] for s in Device.STATUS_CHOICES]
        devices = []
        vendors = ["华为", "戴尔", "HPE", "联想", "Cisco"]
        models_list = ["RH2288", "PowerEdge R750", "ProLiant DL380", "ThinkSystem SR650", "Nexus 9300"]

        for idx, rack in enumerate(racks[:20]):  # 最多20个机柜放设备
            for k in range(1, random.randint(2, 5)):  # 每机柜2-4台设备
                device_type = random.choice(device_types)
                device = Device.objects.create(
                    asset_tag=f"ASSET-{idx*10 + k:04d}",
                    name=f"{device_type.upper()}-{idx*10 + k}",
                    device_type=device_type,
                    model=random.choice(models_list),
                    vendor=random.choice(vendors),
                    serial_number=f"SN{random.randint(100000, 999999)}",
                    rack=rack,
                    position_u=random.randint(1, 38),
                    height_u=1 if device_type == 'switch' else 2,
                    ip_address=f"192.168.{random.randint(10, 30)}.{random.randint(10, 200)}",
                    status=random.choice(statuses),
                    owner=random.choice(users),
                    purchase_date=date.today() - timedelta(days=random.randint(30, 1800)),
                    warranty_expire=date.today() + timedelta(days=random.randint(30, 730))
                )
                devices.append(device)
                self.stdout.write(f"✅ 创建设备: {device.name}")

        # 5. 创建 IP 地址（绑定部分设备）
        used_ips = set()
        for device in devices[:len(devices)//2]:  # 一半设备分配IP
            base_ip = device.ip_address or f"10.0.{random.randint(1, 20)}"
            if not base_ip:
                continue
            try:
                ip_obj = IPAddress.objects.create(
                    ip=base_ip,
                    vlan=str(random.randint(10, 100)),
                    gateway=".".join(base_ip.split(".")[:3]) + ".1",
                    is_used=True,
                    device=device,
                    description=f"管理IP for {device.name}"
                )
                used_ips.add(base_ip)
                self.stdout.write(f"✅ 分配IP: {ip_obj.ip} → {device.name}")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠️ IP冲突或无效: {base_ip} ({e})"))

        # 补充一些未绑定的IP
        for i in range(10):
            ip_str = f"10.10.{random.randint(1, 50)}.{random.randint(1, 254)}"
            if ip_str in used_ips:
                continue
            try:
                IPAddress.objects.create(
                    ip=ip_str,
                    vlan="100",
                    is_used=False,
                    description="预留IP"
                )
                self.stdout.write(f"✅ 创建空闲IP: {ip_str}")
            except:
                pass  # 忽略重复

        # 6. 创建工单
        order_types = [t[0] for t in WorkOrder.ORDER_TYPES]
        statuses_wo = [s[0] for s in WorkOrder.STATUS_CHOICES]
        for device in devices[:10]:  # 前10台设备创建工单
            wo = WorkOrder.objects.create(
                title=f"{random.choice(['紧急', '常规'])}{random.choice(order_types)}任务",
                order_type=random.choice(order_types),
                device=device,
                requester=admin_user,
                assignee=random.choice(users),
                status=random.choice(statuses_wo),
                description=f"自动创建的测试工单 for {device.name}",
                created_at=timezone.now() - timedelta(hours=random.randint(1, 100))
            )
            if wo.status == 'completed':
                wo.completed_at = wo.created_at + timedelta(hours=random.randint(2, 48))
                wo.save()
            self.stdout.write(f"✅ 创建工单: {wo.title}")

        self.stdout.write(
            self.style.SUCCESS(
                "🎉 测试数据生成完成！\n"
                "默认账号:\n"
                "  admin / admin123\n"
                "  user1~user5 / user123"
            )
        )

