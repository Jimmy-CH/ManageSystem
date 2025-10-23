import uuid
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from basic.models import Org, Employee
from xc.models import (
    Product, Application, App,
    Project, Version, Demand,
    Regression, RegressionConnApplication,
    PublishTask, DutyScheduleData
)


class Command(BaseCommand):
    help = '生成 CMDB + CICD 系统示例数据'

    def handle(self, *args, **options):
        self.stdout.write('开始生成 CMDB + CICD 示例数据...')

        # ====== 1. 组织（Org） ======
        root_org, _ = Org.objects.get_or_create(
            org_code='ROOT',
            defaults={
                'id': str(uuid.uuid4()),
                'org_name': '集团总部',
                'unit_name': '集团',
                'unit_code': 'GRP',
                'pk_org_id': 'ROOT',
                'org_full_code': 'ROOT',
                'org_full_name': '集团总部',
                'seal_status': 'N',
                'create_time': timezone.now(),
                'update_time': timezone.now()
            }
        )

        depts = []
        for i in range(1, 4):
            dept_code = f'DEPT{i:02d}'
            dept, _ = Org.objects.get_or_create(
                org_code=dept_code,
                defaults={
                    'id': str(uuid.uuid4()),
                    'org_name': f'技术事业部{i}',
                    'unit_name': '集团',
                    'unit_code': 'GRP',
                    'pk_org_id': dept_code,
                    'parent': root_org,
                    'org_full_code': f'ROOT|{dept_code}',
                    'org_full_name': f'集团总部|技术事业部{i}',
                    'seal_status': 'N',
                    'create_time': timezone.now(),
                    'update_time': timezone.now()
                }
            )
            depts.append(dept)

        # ====== 2. 员工（Employee） ======
        employees = []
        for i in range(1, 21):  # 20 名员工
            psncode = f'U{i:04d}'
            dept = depts[(i - 1) % len(depts)]
            emp, _ = Employee.objects.get_or_create(
                psncode=psncode,
                defaults={
                    'id': str(uuid.uuid4()),
                    'psnname': f'员工{i}',
                    'email': f'user{i}@example.com',
                    'mobile': f'1380000{i:04d}',
                    'dept': dept,
                    'deptname': dept.org_name,
                    'psnclscope': 0,
                    'unitname': '集团',
                    'jobname': '工程师',
                }
            )
            employees.append(emp)

        # ====== 3. Product 树（4 层） ======
        # L1: 部门
        l1 = Product.objects.get_or_create(
            name='智能业务部', level=1, defaults={'owner': employees[0]}
        )[0]

        # L2: 开发组
        l2 = Product.objects.get_or_create(
            name='核心平台组', level=2, parent=l1, defaults={'owner': employees[1]}
        )[0]

        # L3: 产品
        l3 = Product.objects.get_or_create(
            name='星盾平台', level=3, parent=l2, defaults={'owner': employees[2]}
        )[0]

        # L4: 系统
        systems = []
        for i in range(1, 4):
            sys_name = f'星盾子系统{i}'
            sys_obj, _ = Product.objects.get_or_create(
                name=sys_name, level=4, parent=l3, defaults={'owner': employees[i+2]}
            )
            systems.append(sys_obj)

        # ====== 4. Application（CMDB 应用） ======
        apps_cmdb = []
        for i, sys_obj in enumerate(systems):
            app_id = 1000 + i
            app, _ = Application.objects.get_or_create(
                id=app_id,
                defaults={
                    'name': f'app_{sys_obj.name.lower().replace(" ", "_")}',
                    'cname': f'{sys_obj.name}服务',
                    'product': sys_obj,
                    'owner': employees[i % len(employees)],
                }
            )
            apps_cmdb.append(app)

        # ====== 5. App（外部/总部应用） ======
        external_apps = []
        for i in range(2):
            app_id = 2000 + i
            category = 1 if i == 0 else 2
            app, _ = App.objects.get_or_create(
                id=app_id,
                defaults={
                    'name': f'外部应用{i+1}',
                    'system_name': f'系统{i+1}',
                    'category': category,
                    'owner': '张三,李四',
                    'depart_owner': '王五',
                    'leader': '赵总',
                }
            )
            external_apps.append(app)

        # ====== 6. Project + Version + Demand ======
        projects = []
        for i in range(2):
            proj_id = f'PROJ{i+1:02d}'
            proj, _ = Project.objects.get_or_create(
                id=proj_id,
                defaults={
                    'name': f'项目{i+1}',
                    'org': depts[i % len(depts)],
                    'created_at': timezone.now() - timedelta(days=30)
                }
            )
            projects.append(proj)

            # Version
            ver_id = f'VER{i+1:02d}'
            version, _ = Version.objects.get_or_create(
                id=ver_id,
                defaults={
                    'name': f'v1.{i+1}.0',
                    'project': proj,
                    'start_time': timezone.now() - timedelta(days=20)
                }
            )

            # Demand
            for j in range(3):
                demand_id = i * 100 + j + 1
                Demand.objects.get_or_create(
                    id=demand_id,
                    defaults={
                        'demand_num': f'DEM-{demand_id}',
                        'name': f'需求 {demand_id}',
                        'risk_level': j % 4 + 1,
                        'version': version,
                        'is_mobile_demand': j % 2 == 0
                    }
                )

        # ====== 7. Regression + RegressionConnApplication ======
        reg = Regression.objects.create(
            version=Version.objects.first(),
            created_by=employees[0],
            test_owner=employees[1],
            created_time=timezone.now() - timedelta(days=5),
            test_addr='https://test.example.com'
        )

        for app in apps_cmdb[:2]:
            RegressionConnApplication.objects.get_or_create(
                regression=reg,
                application=app,
                defaults={'package_path': f'/pkg/{app.name}.tar.gz'}
            )

        # ====== 8. PublishTask ======
        for i, app in enumerate(apps_cmdb[:2]):
            PublishTask.objects.get_or_create(
                id=f'PUB{i+1:03d}',
                defaults={
                    'task_number': f'TASK-{i+1}',
                    'version': Version.objects.first(),
                    'application': app,
                    'package_path': f'/deploy/{app.name}.zip',
                    'created_by': employees[i],
                    'created_time': timezone.now() - timedelta(days=3),
                    'description': f'发布 {app.cname}',
                    'is_pub_mapping': i % 2 == 0,
                    'is_deleted': False
                }
            )

        # ====== 9. DutyScheduleData ======
        today = datetime.today().date()
        for i in range(7):  # 最近7天
            duty_date = today - timedelta(days=i)
            DutyScheduleData.objects.get_or_create(
                duty_date=duty_date,
                defaults={
                    'duty_content': {
                        "morning": {
                            "psncode": employees[0].psncode,
                            "psnname": employees[0].psnname
                        },
                        "night": {
                            "psncode": employees[1].psncode,
                            "psnname": employees[1].psnname
                        }
                    }
                }
            )

        self.stdout.write(
            self.style.SUCCESS('✅ CMDB + CICD 示例数据生成完成！')
        )
        self.stdout.write(f'  - Org: {Org.objects.count()}')
        self.stdout.write(f'  - Employee: {Employee.objects.count()}')
        self.stdout.write(f'  - Product: {Product.objects.count()}')
        self.stdout.write(f'  - Application (CMDB): {Application.objects.count()}')
        self.stdout.write(f'  - App (External): {App.objects.count()}')
        self.stdout.write(f'  - Project: {Project.objects.count()}')
        self.stdout.write(f'  - Version: {Version.objects.count()}')
        self.stdout.write(f'  - Demand: {Demand.objects.count()}')
        self.stdout.write(f'  - Regression: {Regression.objects.count()}')
        self.stdout.write(f'  - PublishTask: {PublishTask.objects.count()}')
        self.stdout.write(f'  - DutyScheduleData: {DutyScheduleData.objects.count()}')
