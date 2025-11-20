from rest_framework import serializers
from django.db import transaction
from apps.basic.models import (
    Role, RoleConnEmployee, RoleConnOrg, Menu, RoleConnMenu,
    Permission, RoleConnPermission, MenuConnPermission
)


# ======================
# 工具：动态字段控制
# ======================
class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    允许通过 context['fields'] 动态指定返回字段
    """
    def __init__(self, *args, **kwargs):
        # 获取 fields 参数
        fields = self.context.get('fields')
        super().__init__(*args, **kwargs)

        if fields is not None:
            # 删除未指定的字段
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


# ======================
# RoleSerializer
# ======================
class RoleSerializer(DynamicFieldsModelSerializer):
    menus = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    permissions = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)

    class Meta:
        model = Role
        fields = ['id', 'name', 'alias', 'created_time', 'updated_time', 'created_by', 'updated_by',
                  'menus', 'permissions']
        read_only_fields = ['id', 'created_time', 'updated_time']

    def adjust_menus_permissions(self, role_id, menus=None, permissions=None):
        if menus is not None:
            menus = set(menus)
            old_menus = set(RoleConnMenu.objects.filter(role_id=role_id).values_list('menu_id', flat=True))
            to_remove = old_menus - menus
            to_add = menus - old_menus
            if to_remove:
                RoleConnMenu.objects.filter(role_id=role_id, menu_id__in=to_remove).delete()
            if to_add:
                RoleConnMenu.objects.bulk_create([
                    RoleConnMenu(role_id=role_id, menu_id=m) for m in to_add
                ])

        if permissions is not None:
            permissions = set(permissions)
            old_perms = set(RoleConnPermission.objects.filter(role_id=role_id).values_list('permission_id', flat=True))
            to_remove = old_perms - permissions
            to_add = permissions - old_perms
            if to_remove:
                RoleConnPermission.objects.filter(role_id=role_id, permission_id__in=to_remove).delete()
            if to_add:
                RoleConnPermission.objects.bulk_create([
                    RoleConnPermission(role_id=role_id, permission_id=p) for p in to_add
                ])


# ======================
# RoleConnEmployeeSerializer
# ======================
class RoleConnEmployeeSerializer(DynamicFieldsModelSerializer):
    employees = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)
    roles = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)

    class Meta:
        model = RoleConnEmployee
        fields = ['id', 'role', 'employee', 'created_by', 'created_time', 'employees', 'roles']
        read_only_fields = ['id', 'created_time']

    def add_employees(self, role_id, employee_ids, created_by):
        existing = set(
            RoleConnEmployee.objects.filter(role_id=role_id).values_list('employee_id', flat=True)
        )
        to_add = set(employee_ids) - existing
        if to_add:
            RoleConnEmployee.objects.bulk_create([
                RoleConnEmployee(role_id=role_id, employee_id=e, created_by_id=created_by)
                for e in to_add
            ])

    def adjust_employees(self, role_id, employee_ids, created_by):
        existing = set(
            RoleConnEmployee.objects.filter(role_id=role_id).values_list('employee_id', flat=True)
        )
        employee_ids = set(employee_ids)
        to_add = employee_ids - existing
        to_remove = existing - employee_ids

        if to_add:
            RoleConnEmployee.objects.bulk_create([
                RoleConnEmployee(role_id=role_id, employee_id=e, created_by_id=created_by)
                for e in to_add
            ])
        if to_remove:
            RoleConnEmployee.objects.filter(role_id=role_id, employee_id__in=to_remove).delete()


# ======================
# RoleConnOrgSerializer
# ======================
class RoleConnOrgSerializer(DynamicFieldsModelSerializer):
    orgs = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)

    class Meta:
        model = RoleConnOrg
        fields = ['id', 'role', 'org', 'created_by', 'created_time', 'orgs']
        read_only_fields = ['id', 'created_time']

    def adjust_orgs(self, role_id, org_ids, created_by):
        existing = set(RoleConnOrg.objects.filter(role_id=role_id).values_list('org_id', flat=True))
        org_ids = set(org_ids)
        to_add = org_ids - existing
        to_remove = existing - org_ids

        if to_add:
            RoleConnOrg.objects.bulk_create([
                RoleConnOrg(role_id=role_id, org_id=o, created_by_id=created_by) for o in to_add
            ])
        if to_remove:
            RoleConnOrg.objects.filter(role_id=role_id, org_id__in=to_remove).delete()


# ======================
# MenuSerializer
# ======================
class MenuSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Menu
        fields = ['id', 'name', 'level', 'parent', 'kind', 'path', 'component', 'icon', 'order',
                  'is_active', 'is_hidden', 'created_by', 'created_time']
        read_only_fields = ['id', 'created_time']

    def validate(self, attrs):
        kind = attrs.get('kind')
        path = attrs.get('path')
        instance = self.instance

        if kind == 2:  # 菜单类型
            if not path:
                raise serializers.ValidationError('菜单路径参数不能为空')
            qs = Menu.objects.filter(path=path)
            if instance:
                qs = qs.exclude(id=instance.id)
            if qs.exists():
                raise serializers.ValidationError('菜单路径参数不能重复')
        return attrs


# ======================
# RoleConnMenuSerializer
# ======================
class RoleConnMenuSerializer(serializers.Serializer):
    role = serializers.CharField()
    menus = serializers.ListField(child=serializers.IntegerField())

    def adjust(self, role_id, menu_ids):
        existing = set(RoleConnMenu.objects.filter(role_id=role_id).values_list('menu_id', flat=True))
        menu_ids = set(menu_ids)
        to_add = menu_ids - existing
        to_remove = existing - menu_ids

        if to_add:
            RoleConnMenu.objects.bulk_create([
                RoleConnMenu(role_id=role_id, menu_id=m) for m in to_add
            ])
        if to_remove:
            RoleConnMenu.objects.filter(role_id=role_id, menu_id__in=to_remove).delete()


# ======================
# PermissionSerializer
# ======================
class PermissionSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'alias', 'description', 'created_by', 'created_time']
        read_only_fields = ['id', 'created_time']

    # ⚠️ 不建议手动设置 ID！除非你有充分理由（如遗留系统）
    # 如果必须保留，可重写 create，但强烈建议使用数据库自增
    # def create(self, validated_data):
    #     if not Permission.objects.exists():
    #         validated_data['id'] = 100000
    #     else:
    #         last = Permission.objects.order_by('-id').first()
    #         validated_data['id'] = last.id + 1
    #     return super().create(validated_data)


# ======================
# RoleConnPermissionSerializer
# ======================
class RoleConnPermissionSerializer(DynamicFieldsModelSerializer):
    permissions = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)

    class Meta:
        model = RoleConnPermission
        fields = ['id', 'role', 'permission', 'created_by', 'created_time', 'permissions']
        read_only_fields = ['id', 'created_time']

    def adjust_permissions(self, role_id, permission_ids, created_by):
        existing = set(
            RoleConnPermission.objects.filter(role_id=role_id).values_list('permission_id', flat=True)
        )
        permission_ids = set(permission_ids)
        to_add = permission_ids - existing
        to_remove = existing - permission_ids

        if to_add:
            RoleConnPermission.objects.bulk_create([
                RoleConnPermission(role_id=role_id, permission_id=p, created_by_id=created_by)
                for p in to_add
            ])
        if to_remove:
            RoleConnPermission.objects.filter(role_id=role_id, permission_id__in=to_remove).delete()


# ======================
# MenuConnPermissionSerializer
# ======================
class MenuConnPermissionSerializer(serializers.Serializer):
    menu = serializers.CharField()
    permission_name = serializers.CharField()
    permission_alias = serializers.CharField()
    permission = serializers.IntegerField(required=False)

    def add_permission(self, menu_id, name, alias, created_by):
        with transaction.atomic():
            perm = Permission.objects.create(name=name, alias=alias, created_by_id=created_by)
            MenuConnPermission.objects.get_or_create(menu_id=menu_id, permission=perm)

    def delete_permission(self, menu_id, permission_id):
        with transaction.atomic():
            MenuConnPermission.objects.filter(menu_id=menu_id, permission_id=permission_id).delete()
            Permission.objects.filter(id=permission_id).delete()
