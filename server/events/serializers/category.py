# serializers.py
from rest_framework import serializers
from events.models import Category


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    full_path = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'parent',
            'level',
            'order',
            'is_active',
            'created_at',  # 假设 BaseModel 有 created_at
            'updated_at',  # 假设 BaseModel 有 updated_at
            'children',   # 子分类（嵌套）
            'full_path',  # 完整路径名称
        ]

    def get_children(self, obj):
        """返回激活的子分类列表"""
        children = obj.children.filter(is_active=True).order_by('order', 'id')
        return CategorySerializer(children, many=True).data

    def get_full_path(self, obj):
        return obj.get_full_path_name()
