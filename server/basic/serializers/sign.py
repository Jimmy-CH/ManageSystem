from rest_framework import serializers
from basic.models import Sign, SignAPIs
import json


# 自定义字段：验证 JSON 字符串
class JSONStringField(serializers.CharField):
    def to_internal_value(self, data):
        if isinstance(data, str):
            try:
                json.loads(data)
            except (ValueError, TypeError):
                raise serializers.ValidationError("Must be a valid JSON string.")
        elif isinstance(data, (list, dict)):
            # 允许前端传对象，自动转为字符串
            data = json.dumps(data, ensure_ascii=False)
        else:
            raise serializers.ValidationError("Invalid input type for JSON string.")
        return super().to_internal_value(data)

    def to_representation(self, value):
        if value:
            try:
                return json.loads(value)
            except (ValueError, TypeError):
                return value
        return value


class SignAPIsListSerializer(serializers.ModelSerializer):
    """用于嵌套展示的精简版"""
    methods = JSONStringField()

    class Meta:
        model = SignAPIs
        fields = ['id', 'url', 'methods']


class SignAPIsSerializer(serializers.ModelSerializer):
    """完整版，用于创建/更新"""
    methods = JSONStringField()

    class Meta:
        model = SignAPIs
        fields = ['id', 'url', 'methods', 'sign']
        extra_kwargs = {
            'sign': {'write_only': True}  # 通常 sign 是外键，创建时传，展示时不暴露
        }


class SignSerializer(serializers.ModelSerializer):
    apis = SignAPIsListSerializer(many=True, read_only=True)

    class Meta:
        model = Sign
        fields = [
            'id', 'security_key', 'sign_time', 'comment',
            'apply_user', 'application', 'is_active',
            'apply_user_info', 'application_info', 'apis'
        ]
        read_only_fields = ['id', 'security_key', 'sign_time', 'apply_user', 'apply_user_info', 'application_info']

    def create(self, validated_data):
        # 如果需要在创建时关联 apis，需重写逻辑（当前 apis 为 read_only）
        return super().create(validated_data)
