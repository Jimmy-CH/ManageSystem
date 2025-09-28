
from rest_framework import serializers
from .models import Category, SLAStandard, Incident, Fault, User


class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone']


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    full_path_name = serializers.CharField(source='get_full_path_name', read_only=True)

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'parent', 'level', 'order', 'is_active',
            'full_path_name', 'children', 'created_at', 'updated_at'
        ]

    def get_children(self, obj):
        if obj.children.exists():
            return CategorySerializer(obj.children.all(), many=True).data
        return []


class SLAStandardSerializer(serializers.ModelSerializer):
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)

    class Meta:
        model = SLAStandard
        fields = [
            'id', 'level_name', 'priority', 'priority_display',
            'response_time', 'resolve_time', 'description'
        ]
        read_only_fields = ['id']


class FaultSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Fault
        fields = [
            'id', 'incident', 'detail', 'root_cause', 'solution',
            'downtime_minutes', 'impact_scope', 'status', 'status_display',
            'created_at', 'updated_at'
        ]


class IncidentListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    source_display = serializers.CharField(source='get_source_display', read_only=True)
    reporter_name = serializers.CharField(source='reporter.username', read_only=True)
    assignee_name = serializers.CharField(source='assignee.username', read_only=True)
    sla_level = serializers.CharField(source='sla.level_name', read_only=True)
    is_overdue_response = serializers.BooleanField(read_only=True)
    is_overdue_resolve = serializers.BooleanField(read_only=True)
    fault_count = serializers.SerializerMethodField()

    class Meta:
        model = Incident
        fields = [
            'id', 'title', 'description', 'category', 'category_name',
            'priority', 'priority_display', 'source', 'source_display',
            'reporter', 'reporter_name', 'assignee', 'assignee_name',
            'status', 'status_display', 'occurred_at', 'responded_at', 'resolved_at',
            'sla', 'sla_level', 'is_active',
            'is_overdue_response', 'is_overdue_resolve', 'fault_count',
            'created_at', 'updated_at'
        ]

    def get_fault_count(self, obj):
        return obj.faults.count()


class IncidentDetailSerializer(IncidentListSerializer):
    faults = FaultSerializer(many=True, read_only=True)

    class Meta(IncidentListSerializer.Meta):
        fields = IncidentListSerializer.Meta.fields + ['faults']


class IncidentCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = [
            'title', 'description', 'category', 'priority', 'source',
            'reporter', 'assignee', 'status', 'occurred_at',
            'responded_at', 'resolved_at', 'sla', 'is_active'
        ]


class CategoryTreeSerializer(serializers.ModelSerializer):
    parent_id = serializers.IntegerField(source='parent.id', read_only=True, allow_null=True)
    full_path_name = serializers.CharField(source='get_full_path_name', read_only=True)  # ✅ 绑定方法
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'level', 'parent_id', 'full_path_name', 'children', 'order', 'is_active']

    def get_children(self, obj):
        if hasattr(obj, '_children_list'):
            # 使用预构建的子节点（推荐）
            return CategoryTreeSerializer(obj._children_list, many=True).data
        else:
            # 降级方案：查询数据库（有N+1风险）
            return CategoryTreeSerializer(obj.children.all(), many=True).data
