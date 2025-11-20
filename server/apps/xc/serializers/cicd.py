"""
序列化器模块：项目、版本、发布任务、需求、回归测试等
"""
from rest_framework.serializers import ModelSerializer
from apps.xc.models import Project, Version, PublishTask, Demand, Regression, RegressionConnApplication


# 导出
__all__ = [
    'ProjectSerializer',
    'VersionSerializer',
    'PublishTaskSerializer',
    'DemandSerializer',
    'RegressionSerializer',
    'RegressionConnApplicationSerializer'
]


class DynamicFieldsModelSerializer(ModelSerializer):
    """
    支持动态字段控制的基类序列化器。
    使用方式：
      - 在 ViewSet 中通过 context 传入 fields 列表；
      - 或在 Meta 中定义 field_sets 字典，配合 view.action 自动匹配。
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 1. 优先：显式指定 fields（通过 context={'fields': [...]})
        fields = self.context.get('fields')
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
            return

        # 2. 次选：根据 view.action 匹配 Meta.field_sets
        view = self.context.get('view')
        if not view:
            return

        action = getattr(view, 'action', None)
        meta = getattr(self.Meta, 'field_sets', None)
        if not meta or not isinstance(meta, dict):
            return

        # 支持 action 名直接匹配（如 'list', 'retrieve'）
        # 也支持自定义 action 如 'relate_component'，但通常由调用方传 fields 更清晰
        if action in meta:
            allowed = set(meta[action])
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class ProjectSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name']


class VersionSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Version
        fields = ['id', 'name']


class PublishTaskSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = PublishTask
        # 必须包含所有可能用到的字段（包括 relate_component 和 relate_testask 中的）
        fields = [
            'id', 'application_name', 'application_cname', 'system_name', 'created_time',
            'application_owner', 'product_name', 'create_user_info', 'task_number',
            'is_pubnet_mapping'
        ]
        field_sets = {
            'relate_component': [
                'id', 'application_name', 'application_cname', 'system_name', 'created_time',
                'application_owner'
            ],
            'relate_testask': [
                'product_name', 'system_name', 'application_name', 'create_user_info',
                'created_time', 'task_number', 'is_pubnet_mapping'
            ]
        }


class DemandSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Demand
        fields = ['name', 'description', 'risk_level_info']
        field_sets = {
            'relate_version': ['name', 'description', 'risk_level_info']
        }


class RegressionSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Regression
        fields = ['id', 'test_addr', 'test_owner_info']
        field_sets = {
            'relate_testask': ['id', 'test_addr', 'test_owner_info']
        }


class RegressionConnApplicationSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = RegressionConnApplication
        fields = [
            'product_name', 'system_name', 'application_name', 'create_user_info',
            'created_time', 'task_number', 'is_pubnet_mapping'
        ]
        field_sets = {
            'relate_testask': [
                'product_name', 'system_name', 'application_name', 'create_user_info',
                'created_time', 'task_number', 'is_pubnet_mapping'
            ]
        }
