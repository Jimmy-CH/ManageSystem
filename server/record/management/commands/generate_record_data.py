
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import random

# 安全检查：禁止在生产环境运行
if not settings.DEBUG:
    raise RuntimeError("禁止在非 DEBUG 模式下运行此命令！")

from record.models import OAInfo, OAPerson, ProcessRecord, EntryLog


def random_aware_datetime(start_days=-30, end_days=7):
    """
    生成一个带时区信息的随机 datetime（aware datetime）
    范围：从当前时间往前 start_days 天，到往后 end_days 天
    """
    now = timezone.now()
    # 随机天数（包含负数）
    days = random.randint(start_days, end_days)
    # 随机小时和分钟
    hours = random.randint(0, 23)
    minutes = random.randint(0, 59)
    random_delta = timedelta(days=days, hours=hours, minutes=minutes)
    return now + random_delta


class Command(BaseCommand):
    help = '生成测试用的 OA 申请、人员、进出记录及日志（带时区支持）'

    def add_arguments(self, parser):
        parser.add_argument(
            '--oa-count',
            type=int,
            default=10,
            help='要生成的 OA 申请数量（默认: 10）'
        )
        parser.add_argument(
            '--persons-per-oa',
            type=int,
            default=2,
            help='每个 OA 申请关联的人员数（默认: 2）'
        )

    def handle(self, *args, **options):
        from faker import Faker
        fake = Faker('zh_CN')

        oa_count = options['oa_count']
        persons_per_oa = options['persons_per_oa']

        self.stdout.write(
            self.style.SUCCESS(f'开始生成 {oa_count} 个 OA 申请，每个含 {persons_per_oa} 人...')
        )

        for _ in range(oa_count):
            # 生成带时区的时间
            apply_enter = random_aware_datetime(-30, 7)
            apply_leave = apply_enter + timedelta(days=random.randint(1, 10))
            applicant_time = random_aware_datetime(-30, 0)  # 申请时间不晚于现在

            oa_info = OAInfo.objects.create(
                applicant=fake.name(),
                apply_enter_time=apply_enter,
                apply_leave_time=apply_leave,
                apply_count=random.randint(1, 5),
                connected_count=0,
                is_post_entry=random.choice([True, False]),
                oa_link=fake.url() if random.choice([True, False]) else None,
                oa_link_info=fake.sentence()[:100] if random.choice([True, False]) else None,
                is_linked=random.choice([True, False]),
                applicant_time=applicant_time,
            )

            for _ in range(persons_per_oa):
                person = OAPerson.objects.create(
                    person_name=fake.name(),
                    phone_number=fake.phone_number(),
                    person_type=random.choice([1, 2]),
                    id_type=random.choice([1, 2, 3, 4]),
                    id_number=fake.ssn()[:18] if random.choice([True, False]) else fake.license_plate(),
                    unit=random.choice(['蛟龙集团总部', '技术研发中心', '市场部', '外部合作公司A']),
                    department=random.choice(['软件开发部', '运维部', '人力资源', '财务部']),
                    is_linked=random.choice([True, False]),
                    oa_info=oa_info,
                )

                # 实际进入/离开时间：可能为空，也可能在 apply_enter 之后
                entered = None
                exited = None
                if random.choice([True, False]):
                    entered = apply_enter + timedelta(minutes=random.randint(0, 120))
                    if random.choice([True, False]):
                        exited = entered + timedelta(hours=random.randint(1, 8))

                record = ProcessRecord.objects.create(
                    applicant=oa_info.applicant,
                    person_name=person.person_name,
                    phone_number=person.phone_number,
                    person_type=person.person_type,
                    id_type=person.id_type,
                    id_number=person.id_number,
                    unit=person.unit,
                    department=person.department,
                    registration_status=random.choice([1, 2, 3]),
                    apply_enter_time=oa_info.apply_enter_time,
                    apply_leave_time=oa_info.apply_leave_time,
                    entered_time=entered,
                    exited_time=exited,
                    enter_count=1,
                    companion=random.choice(['张三', '李四', '王五', '无']),
                    reason=fake.sentence(nb_words=6),
                    carried_items=fake.sentence(nb_words=4),
                    card_status=random.choice([1, 2, 3, 4]),
                    card_type=random.choice([1, 2, 3, 4, 5]),
                    pledged_status=random.choice([1, 2, 3, 4]),
                    remarks=fake.text(max_nb_chars=100) if random.choice([True, False]) else None,
                    oa_link=oa_info.oa_link,
                    is_emergency=False,
                    is_normal=True,
                    is_linked=True,
                    oa_link_info=oa_info.oa_link_info,
                    applicant_time=oa_info.applicant_time,
                )

                EntryLog.objects.create(
                    process_record=record,
                    entered_time=record.entered_time or timezone.now(),
                    exited_time=record.exited_time or (timezone.now() + timedelta(hours=3)),
                    create_time=timezone.now(),
                    create_user_code=fake.user_name(),
                    create_user_name=fake.name(),
                    card_status=record.card_status,
                    card_type=record.card_type,
                    pledged_status=record.pledged_status,
                    id_type=record.id_type,
                    remarks=record.remarks,
                    is_normal=record.is_normal,
                    operation=random.choice(['入场', '离场']),
                    companion=record.companion,
                )

        self.stdout.write(
            self.style.SUCCESS(f'✅ 成功生成 {oa_count} 个 OA 申请及相关数据！')
        )
