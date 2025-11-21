from rest_framework import serializers
from apps.basic.models import Employee, Org, Menu, RoleConnMenu, Permission, RoleConnPermission
from apps.basic.utils import fetch_menu_tree, split_and_concat_last_three


__all__ = ['EmployeeSerializer', 'OrgSerializer']


class EmployeeSerializer(serializers.ModelSerializer):
    menus_tree = serializers.SerializerMethodField()
    permission_alias_list = serializers.SerializerMethodField()
    psnname_psncode = serializers.SerializerMethodField()

    def get_psnname_psncode(self, obj):
        return f'{obj.psnname}({obj.psncode})'

    def _get_user_role_aliases(self, obj):
        """获取用户所有角色别名（含默认和部门角色）"""
        role_aliases = {'default-users'}

        # 用户直接关联的角色
        role_aliases.update(obj.roles.values_list('alias', flat=True))

        # 部门关联的角色（确保 deptcode 存在）
        if hasattr(obj, 'deptcode') and obj.deptcode:
            role_aliases.update(obj.deptcode.roles.values_list('alias', flat=True))

        return role_aliases

    def get_menus_tree(self, obj):
        role_aliases = self._get_user_role_aliases(obj)

        if 'admin' in role_aliases:
            menus_qs = Menu.objects.all()
        else:
            menu_ids = RoleConnMenu.objects.filter(
                role__alias__in=role_aliases
            ).values_list('menu_id', flat=True)
            menus_qs = Menu.objects.filter(id__in=menu_ids)

        menus = menus_qs.order_by('order').values(
            'id', 'name', 'path', 'component', 'icon', 'order', 'is_hidden', 'parent'
        )

        return fetch_menu_tree(menus=list(menus))

    def get_permission_alias_list(self, obj):
        role_aliases = self._get_user_role_aliases(obj)

        if 'admin' in role_aliases:
            alias_list = Permission.objects.values_list('alias', flat=True)
        else:
            alias_list = RoleConnPermission.objects.filter(
                role__alias__in=role_aliases
            ).values_list('permission__alias', flat=True).distinct()

        return list(alias_list)

    class Meta:
        model = Employee
        # 注意：以下字段仅为文档或前端约定，DRF 原生不识别
        # 实际序列化字段由 `fields` 决定
        fields = [
            'id', 'psncode', 'psnname', 'org_name', 'org_full_name',
            'mobile', 'outdutydate',
            'menus_tree', 'permission_alias_list', 'psnname_psncode'
        ]
        # 可根据需要动态裁剪字段（见下方可选扩展）


class OrgSerializer(serializers.ModelSerializer):
    org_chain = serializers.SerializerMethodField()

    def get_org_chain(self, obj):
        return split_and_concat_last_three(obj.org_full_name)

    class Meta:
        model = Org
        fields = [
            'id', 'pk_org_id', 'org_code', 'org_name', 'unit_name',
            'unit_code', 'parent_info', 'org_full_code', 'org_full_name',
            'create_time', 'update_time', 'org_chain'
        ]

