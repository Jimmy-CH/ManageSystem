import uuid
from django.core.management.base import BaseCommand
from django.utils import timezone
from basic.models import Org, Employee, Menu, Permission, Role
from basic.models import (
    RoleConnEmployee, RoleConnOrg, RoleConnMenu,
    RoleConnPermission, MenuConnPermission
)


class Command(BaseCommand):
    help = '生成多条基础权限系统示例数据'

    def handle(self, *args, **options):
        self.stdout.write('开始批量生成示例数据...')

        # ====== 1. 组织架构（3层） ======
        units = ['星盾集团', '未来科技', '云智公司']
        divisions = ['技术研发中心', '产品运营中心', '数据智能中心']
        depts = ['前端组', '后端组', '测试组', '运维组', '算法组']

        orgs = []
        for i, unit in enumerate(units):
            unit_code = f'U{i+1:02d}'
            root_org, _ = Org.objects.get_or_create(
                org_code=unit_code,
                defaults={
                    'id': str(uuid.uuid4()),
                    'org_name': unit,
                    'unit_name': unit,
                    'unit_code': unit_code,
                    'pk_org_id': unit_code,
                    'org_full_code': unit_code,
                    'org_full_name': unit,
                    'seal_status': 'N',
                    'create_time': timezone.now(),
                    'update_time': timezone.now()
                }
            )
            orgs.append(root_org)

            for j, div in enumerate(divisions):
                div_code = f'{unit_code}D{j+1:02d}'
                division, _ = Org.objects.get_or_create(
                    org_code=div_code,
                    defaults={
                        'id': str(uuid.uuid4()),
                        'org_name': div,
                        'unit_name': unit,
                        'unit_code': unit_code,
                        'pk_org_id': div_code,
                        'parent': root_org,
                        'org_full_code': f'{unit_code}|{div_code}',
                        'org_full_name': f'{unit}|{div}',
                        'seal_status': 'N',
                        'create_time': timezone.now(),
                        'update_time': timezone.now()
                    }
                )
                orgs.append(division)

                for k, dept in enumerate(depts[:3]):  # 每个事业部下3个部门
                    dept_code = f'{div_code}T{k+1:02d}'
                    department, _ = Org.objects.get_or_create(
                        org_code=dept_code,
                        defaults={
                            'id': str(uuid.uuid4()),
                            'org_name': dept,
                            'unit_name': unit,
                            'unit_code': unit_code,
                            'pk_org_id': dept_code,
                            'parent': division,
                            'org_full_code': f'{unit_code}|{div_code}|{dept_code}',
                            'org_full_name': f'{unit}|{div}|{dept}',
                            'seal_status': 'N',
                            'create_time': timezone.now(),
                            'update_time': timezone.now()
                        }
                    )
                    orgs.append(department)

        # ====== 2. 员工（每个部门3~5人） ======
        employees = []
        emp_counter = 1
        for org in orgs:
            if '组' in org.org_name:  # 只在最底层部门加员工
                num_employees = 3 + (emp_counter % 3)  # 3~5人
                for n in range(num_employees):
                    psncode = f'EMP{emp_counter:04d}'
                    emp, _ = Employee.objects.get_or_create(
                        psncode=psncode,
                        defaults={
                            'id': str(uuid.uuid4()),
                            'psnname': f'员工{emp_counter}',
                            'email': f'emp{emp_counter}@example.com',
                            'mobile': f'1380000{emp_counter:04d}',
                            'dept': org,
                            'deptname': org.org_name,
                            'psnclscope': 0,
                            'unitname': org.unit_name,
                            'jobname': '工程师' if n < 2 else '实习生',
                        }
                    )
                    employees.append(emp)
                    emp_counter += 1

        # ====== 3. 菜单（3级结构） ======
        menu_root, _ = Menu.objects.get_or_create(
            name='系统平台',
            defaults={'level': 1, 'kind': 1, 'order': 0, 'is_active': True}
        )

        menu_modules = ['用户中心', '权限管理', '业务系统', '数据分析']
        menus = [menu_root]
        permission_list = []

        for idx, mod_name in enumerate(menu_modules):
            mod_menu, _ = Menu.objects.get_or_create(
                name=mod_name,
                parent=menu_root,
                defaults={
                    'level': 2,
                    'kind': 1,
                    'order': idx + 1,
                    'is_active': True,
                    'path': f'/module{idx+1}'
                }
            )
            menus.append(mod_menu)

            sub_menus = [f'{mod_name}列表', f'{mod_name}配置', f'{mod_name}日志']
            for sidx, sub_name in enumerate(sub_menus):
                sub_menu, _ = Menu.objects.get_or_create(
                    name=sub_name,
                    parent=mod_menu,
                    defaults={
                        'level': 3,
                        'kind': 2,
                        'order': sidx + 1,
                        'is_active': True,
                        'path': f'/module{idx+1}/sub{sidx+1}',
                        'component': f'{mod_name.replace(" ", "")}Sub{sidx+1}'
                    }
                )
                menus.append(sub_menu)

                # 为每个叶子菜单创建2个权限：view + edit
                for perm_type in ['view', 'edit']:
                    alias = f"{mod_name.lower().replace(' ', '_')}:{sub_name.lower().replace(' ', '_')}:{perm_type}"
                    perm, _ = Permission.objects.get_or_create(
                        alias=alias,
                        defaults={
                            'name': f'{sub_name} - {perm_type}',
                            'description': f'允许{perm_type}操作'
                        }
                    )
                    permission_list.append((sub_menu, perm, perm_type == 'view'))

        # ====== 4. 菜单绑定权限（一对一）——仅绑定 view 权限作为菜单入口 ======
        for menu_obj, perm_obj, is_view in permission_list:
            if is_view:
                MenuConnPermission.objects.get_or_create(
                    menu=menu_obj,
                    defaults={'permission': perm_obj, 'created_by': employees[0]}
                )

        # ====== 5. 角色 ======
        roles = {}
        for role_name, alias in [('系统管理员', 'admin'), ('部门经理', 'manager'), ('普通员工', 'viewer')]:
            role, _ = Role.objects.get_or_create(
                alias=alias,
                defaults={'name': role_name}
            )
            roles[alias] = role

        # ====== 6. 建立关联 ======
        admin_role = roles['admin']
        manager_role = roles['manager']
        viewer_role = roles['viewer']

        all_permissions = list(Permission.objects.all())
        all_menus = Menu.objects.filter(kind=2)  # 只关联叶子菜单

        # 6.1 角色-权限
        # admin: 所有权限
        for perm in all_permissions:
            RoleConnPermission.objects.get_or_create(
                role=admin_role, permission=perm,
                defaults={'created_by': employees[0]}
            )

        # manager: 所有 view + 部分 edit
        view_perms = [p for p in all_permissions if ':view' in p.alias]
        edit_perms = [p for p in all_permissions if ':edit' in p.alias][:len(view_perms)//2]
        for perm in view_perms + edit_perms:
            RoleConnPermission.objects.get_or_create(
                role=manager_role, permission=perm,
                defaults={'created_by': employees[0]}
            )

        # viewer: 仅 view
        for perm in view_perms:
            RoleConnPermission.objects.get_or_create(
                role=viewer_role, permission=perm,
                defaults={'created_by': employees[0]}
            )

        # 6.2 角色-菜单
        for menu in all_menus:
            RoleConnMenu.objects.get_or_create(
                role=admin_role, menu=menu,
                defaults={'created_by': employees[0]}
            )
            RoleConnMenu.objects.get_or_create(
                role=manager_role, menu=menu,
                defaults={'created_by': employees[0]}
            )
            RoleConnMenu.objects.get_or_create(
                role=viewer_role, menu=menu,
                defaults={'half_checked': False, 'created_by': employees[0]}
            )

        # 6.3 角色-员工（按规则分配）
        for i, emp in enumerate(employees):
            if i == 0:
                role = admin_role
            elif i % 10 == 0:  # 每10人一个经理
                role = manager_role
            else:
                role = viewer_role
            RoleConnEmployee.objects.get_or_create(
                role=role, employee=emp,
                defaults={'created_by': employees[0]}
            )

        # 6.4 角色-组织（admin 拥有所有根组织）
        for org in Org.objects.filter(parent__isnull=True):
            RoleConnOrg.objects.get_or_create(
                role=admin_role, org=org,
                defaults={'created_by': employees[0]}
            )

        self.stdout.write(
            self.style.SUCCESS(f'✅ 批量数据生成完成！')
        )
        self.stdout.write(f'  - 组织数量: {Org.objects.count()}')
        self.stdout.write(f'  - 员工数量: {Employee.objects.count()}')
        self.stdout.write(f'  - 菜单数量: {Menu.objects.count()}')
        self.stdout.write(f'  - 权限数量: {Permission.objects.count()}')
        self.stdout.write(f'  - 角色数量: {Role.objects.count()}')
