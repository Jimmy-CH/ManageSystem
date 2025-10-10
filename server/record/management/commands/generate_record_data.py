
import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from record.models import OAInfo, OAPerson, ProcessRecord, EntryLog


class Command(BaseCommand):
    help = 'Generate test data for OAInfo, OAPerson, ProcessRecord, and EntryLog'

    def handle(self, *args, **options):
        self.stdout.write("开始生成测试数据...")

        # ===== 1. 生成后补流程（OAInfo + OAPerson）=====
        applicants = ["张三", "李四", "王五", "赵六", "孙七"]
        units = ["蛟龙集团IT部", "外部供应商A", "外部供应商B", "数据中心运维组", "安全审计部"]
        departments = ["运维部", "开发部", "安全部", "外包管理", "基础设施"]
        id_types = ["工牌", "身份证", "驾驶证", "护照"]
        id_numbers = [
            "EMP2024001", "110101199001011234", "京A12345", "E12345678",
            "EMP2024002", "110101199102022345", "沪B67890", "E87654321"
        ]

        for i in range(5):
            applicant = applicants[i % len(applicants)]
            now = timezone.now()
            enter_time = now - timedelta(days=random.randint(1, 7), hours=random.randint(0, 23))
            leave_time = enter_time + timedelta(hours=random.randint(2, 12))

            oa_info = OAInfo.objects.create(
                applicant=applicant,
                apply_enter_time=enter_time,
                apply_leave_time=leave_time,
                apply_count=random.randint(1, 5),
                connected_count=0,
                is_post_entry=True,
                oa_link=f"https://oa.example.com/process/{1000 + i}"
            )

            person_count = random.randint(1, 3)
            for j in range(person_count):
                id_type_str = random.choice(id_types)
                id_type = {"工牌": 1, "身份证": 2, "驾驶证": 3, "护照": 4}[id_type_str]
                person_type = 1 if id_type == 1 else 2
                id_number = random.choice(id_numbers)

                OAPerson.objects.create(
                    oa_info=oa_info,
                    name=f"{applicant}团队成员{j+1}",
                    phone_number=f"138{random.randint(10000000, 99999999)}",
                    person_type=person_type,
                    id_type=id_type,
                    id_number=id_number,
                    unit=random.choice(units),
                    department=random.choice(departments),
                    is_linked=False
                )

        self.stdout.write(self.style.SUCCESS("✅ 已生成 5 条后补流程数据"))

        # ===== 2. 生成正常流程（ProcessRecord）=====
        reasons = ["设备巡检", "服务器维护", "网络调试", "安全检查", "数据迁移"]
        items = ["笔记本电脑", "U盘", "工具箱", "测试设备", "无"]

        for i in range(10):
            applicant = random.choice(applicants)
            enter_time = timezone.now() + timedelta(days=random.randint(-3, 3), hours=random.randint(0, 23))
            leave_time = enter_time + timedelta(hours=random.randint(1, 8))

            record = ProcessRecord.objects.create(
                applicant=applicant,
                name=f"正常流程人员{i+1}",
                phone_number=f"139{random.randint(10000000, 99999999)}",
                person_type=random.choice([1, 2]),
                id_type=random.choice([1, 2, 3, 4]),
                id_number=random.choice(id_numbers),
                unit=random.choice(units),
                department=random.choice(departments),
                status=random.choice([1, 2, 3]),  # 未入场/已入场/已离场
                apply_enter_time=enter_time,
                apply_leave_time=leave_time,
                entered_time=enter_time if random.random() > 0.5 else None,
                exited_time=leave_time if random.random() > 0.7 else None,
                enter_count=1,
                companion="无" if random.random() > 0.3 else "管理员老刘",
                reason=random.choice(reasons),
                carried_items=random.choice(items),
                card_status=random.choice([1, 2, 3]),
                card_type=random.randint(1, 5),
                pledged_status=random.choice([1, 2, 3]),
                remarks="",
                oa_link="",
                is_emergency=False,
                is_normal=True,
                is_linked=True,
                create_user="admin",
                update_user="admin"
            )

            # ===== 3. 为部分记录生成 EntryLog =====
            if random.random() > 0.4:  # 60% 概率生成日志
                EntryLog.objects.create(
                    process_record=record,
                    entered_time=record.entered_time or (record.apply_enter_time if random.random() > 0.5 else None),
                    exited_time=record.exited_time or (record.apply_leave_time if random.random() > 0.5 else None),
                    create_user="admin",
                    update_user="admin",
                    card_status=record.card_status,
                    card_type=record.card_type,
                    pledged_status=record.pledged_status,
                    id_type=record.id_type,
                    remarks="自动生成测试日志"
                )

        self.stdout.write(self.style.SUCCESS("✅ 已生成 10 条正常流程记录及部分进出日志"))

        self.stdout.write(self.style.SUCCESS("🎉 测试数据生成完成！"))
