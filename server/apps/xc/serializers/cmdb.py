"""
产品与应用序列化器
"""
from rest_framework.serializers import ModelSerializer

from apps.xc.models import Product, Application

__all__ = ['ProductSerializer', 'ApplicationSerializer']


class DynamicFieldsModelSerializer(ModelSerializer):
    """
    支持动态字段的基类序列化器。
    自动根据 view.action 匹配 Meta.field_sets 中的字段配置。
    也支持通过 context={'fields': [...]} 显式指定字段。
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 1. 优先：显式传入 fields（用于自定义场景）
        fields = self.context.get('fields')
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
            return

        # 2. 根据 view.action 自动匹配字段集
        view = self.context.get('view')
        if not view:
            return

        action = getattr(view, 'action', None)
        meta = getattr(self.Meta, 'field_sets', None)
        if not meta or not isinstance(meta, dict):
            return

        # 映射 action 到字段集名称
        action_to_fieldset = {
            'list': 'list_fields',
            'retrieve': 'retrieve_fields',
        }

        # 默认使用 action 名作为 key（支持自定义 action 如 'simple_list'）
        fieldset_key = action_to_fieldset.get(action, action)

        if fieldset_key in meta:
            allowed = set(meta[fieldset_key])
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


# ========================
# 序列化器定义
# ========================

class ProductSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'owner_info']  # 必须包含所有可能用到的字段
        field_sets = {
            'simple_list_fields': ['id', 'name'],
            'list_fields': ['id', 'name', 'owner_info'],
            # 可选：为 list/retrieve 显式映射
            'list': ['id', 'name', 'owner_info'],
            'retrieve': ['id', 'name', 'owner_info'],
        }


class ApplicationSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Application
        # 注意：必须包含 list_fields / retrieve_fields / relate_component_fields 中的所有字段
        fields = [
            'id', 'name', 'cname', 'product', 'owner',
            'system_name', 'owner_info', 'depart_owner_info'
        ]
        field_sets = {
            'simple_list_fields': ['id', 'name', 'cname'],
            'list_fields': ['id', 'name', 'cname', 'system_name', 'owner_info', 'depart_owner_info'],
            'retrieve_fields': ['id', 'name', 'cname', 'owner_info'],
            'relate_component_fields': ['name', 'system_name'],

            # 可选：为标准 DRF action 提供默认映射
            'list': ['id', 'name', 'cname', 'system_name', 'owner_info', 'depart_owner_info'],
            'retrieve': ['id', 'name', 'cname', 'owner_info'],
        }

