from rest_framework import serializers
from django.utils import timezone
from apps.basic.models import OperateLog


__all__ = ['OperateLogSerializer']


class OperateLogSerializer(serializers.ModelSerializer):
    # 可选：将 operate_user 显示为用户名（只读）
    operate_user_info = serializers.SerializerMethodField()

    def get_operate_user_info(self, obj):
        if obj.operate_user:
            return {
                'id': obj.operate_user.id,
                'username': obj.operate_user.username,
                'name': getattr(obj.operate_user, 'name', obj.operate_user.username),
            }
        return None

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data.update({
            'operate_user': request.user if request else None,
            'operate_time': timezone.now(),
        })
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context.get('request')
        validated_data.update({
            'operate_user': request.user if request else None,
            'operate_time': timezone.now(),
        })
        return super().update(instance, validated_data)

    class Meta:
        model = OperateLog
        fields = [
            'id', 'instance', 'instance_id', 'operate',
            'operate_user', 'operate_time', 'operate_user_info'
        ]
        read_only_fields = ['id', 'operate_user', 'operate_time']


