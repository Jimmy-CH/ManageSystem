
from rest_framework import serializers
from django.contrib.auth.models import User
from accounts.models import CustomPermission, Role, UserRole


class CustomPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomPermission
        fields = ['id', 'codename', 'name', 'description', 'app_label', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']   # 创建和更新时间由系统管理

    def validate_codename(self, value):
        # 确保 codename 只包含字母、数字、下划线和连字符
        if not value.replace('_', '').replace('-', '').isalnum():
            raise serializers.ValidationError("权限标识符只能包含字母、数字、下划线(_)和连字符(-)。")
        return value


class RoleSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(
        queryset=CustomPermission.objects.all(),
        many=True,
        required=False,
        help_text="权限ID列表"
    )
    permission_details = CustomPermissionSerializer(source='permissions', many=True, read_only=True, help_text="权限详情")

    class Meta:
        model = Role
        fields = [
            'id', 'name', 'description', 'permissions', 'permission_details',
            'is_system', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_system'] # is_system 通常由系统创建时设定

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # 如果是创建或更新操作，可能不需要返回完整的 permission_details
        # 但为了GET请求方便，这里选择返回。可以根据需求调整。
        return data


class UserRoleSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all())
    username = serializers.CharField(source='user.username', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)

    class Meta:
        model = UserRole
        fields = [
            'id', 'user', 'username', 'role', 'role_name',
            'assigned_at', 'expires_at', 'assigned_by', 'notes'
        ]
        read_only_fields = ['assigned_at', 'assigned_by'] # assigned_by 通常由系统填充

    def create(self, validated_data):
        # 自动设置 assigned_by 为当前请求用户
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['assigned_by'] = request.user
        return super().create(validated_data)
