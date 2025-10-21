from rest_framework.serializers import ModelSerializer

from xc.models import App

__all__ = ['AppSerializer']


class AppSerializer(ModelSerializer):
    # 如果 category_info、created_by_info 等是方法字段或嵌套序列化器，
    # 需在此显式定义（示例仅保留字段名，实际需按需实现）
    # 例如：
    # category_info = serializers.SerializerMethodField()
    # created_by_info = UserSimpleSerializer(source='created_by', read_only=True)

    class Meta:
        model = App
        fields = [
            'id', 'name', 'system_name', 'category', 'owner',
            'depart_owner', 'leader', 'created_by', 'updated_by'
        ]
        # 注意：list_fields / retrieve_fields 不是 DRF 原生属性，需通过 context 控制

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 获取上下文中的视图 action（如 'list', 'retrieve'）
        view = self.context.get('view')
        if view:
            action = getattr(view, 'action', None)
            if action == 'list':
                self._filter_fields(['id', 'name', 'system_name', 'category_info',
                                     'owner', 'depart_owner', 'leader',
                                     'created_by_info', 'updated_by_info'])
            elif action == 'retrieve':
                self._filter_fields(['id', 'name', 'system_name', 'category_info',
                                     'owner', 'depart_owner', 'leader',
                                     'created_by_info', 'updated_by_info'])

    def _filter_fields(self, allowed_fields):
        """仅保留 allowed_fields 中存在的字段（忽略不存在的）"""
        existing_fields = set(self.fields)
        allowed = set(allowed_fields)
        for field_name in existing_fields - allowed:
            self.fields.pop(field_name)


