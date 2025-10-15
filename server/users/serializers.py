
from rest_framework import serializers
from .models import User, Role, CustomPermission
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
import logging

logger = logging.getLogger(__name__)


class CustomPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomPermission
        fields = "__all__"


class RolePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomPermission
        fields = ['id', 'name']


class RoleSerializer(serializers.ModelSerializer):
    permission_ids = serializers.PrimaryKeyRelatedField(
        source='permissions',
        queryset=CustomPermission.objects.only('id'),
        many=True,
        write_only=True,
        required=False
    )
    permissions = RolePermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = "__all__"

    def update(self, instance, validated_data):
        # 可选：实现“不传 permission_ids 就不更新权限”
        permissions = validated_data.pop('permissions', None)

        role = super().update(instance, validated_data)

        if permissions is not None:
            role.permissions.set(permissions)

        return role


class UserSerializer(serializers.ModelSerializer):
    role_ids = serializers.PrimaryKeyRelatedField(
        source='roles',
        queryset=Role.objects.all(),
        many=True,
        write_only=True,
        required=False
    )
    roles = RoleSerializer(many=True, read_only=True)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'phone', 'department', 'position', 'avatar', 'status',
                  'role_ids', 'roles', 'create_time', 'update_time', 'importance']

    def create(self, validated_data):
        roles = validated_data.pop('roles', [])
        password = validated_data.pop('password', None)

        standard_fields = {'username', 'email'}
        custom_fields = {}

        for field in list(validated_data.keys()):
            if field not in standard_fields:
                custom_fields[field] = validated_data.pop(field)

        try:
            user = User.objects.create_user(
                username=validated_data.get('username'),
                email=validated_data.get('email', ''),
                password=password  # ← 直接传 password，create_user 会自动加密
            )

            for attr, value in custom_fields.items():
                setattr(user, attr, value)
            user.save()

            user.roles.set(roles)

        except Exception as e:
            print(f"[User Create Failed] data: {validated_data}, custom: {custom_fields}, error: {str(e)}")
            raise serializers.ValidationError(f"创建用户失败: {str(e)}")

        return user

    def update(self, instance, validated_data):
        roles = validated_data.pop('roles', None)
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        try:
            instance.save()
        except Exception as e:
            logger.error(f"[User Update Failed] instance: {instance.id}, data: {validated_data}, error: {str(e)}")
            raise serializers.ValidationError(f"更新用户失败: {str(e)}")

        if roles is not None:
            instance.roles.set(roles)

        return instance


class RegisterSerializer(serializers.ModelSerializer):
    """
    注册序列化器
    """
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'password', 'confirm_password']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("两次密码不一致")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """
    登录序列化器
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("用户名或密码错误")
        if not user.is_active:
            raise serializers.ValidationError("用户已被禁用")

        data['user'] = user
        return data


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    自定义 Token 返回用户信息
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # 添加自定义字段到 token payload
        token['username'] = user.username
        token['email'] = user.email
        token['is_staff'] = user.is_staff
        token['is_superuser'] = user.is_superuser
        # 如果你有 roles 权限系统
        token['roles'] = [role.name for role in user.roles.all()]
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # 在返回的 data 中添加用户信息
        serializer = UserSerializer(self.user).data
        data['user'] = serializer
        return data
