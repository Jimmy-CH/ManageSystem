
from rest_framework import serializers
from .models import User, Role, CustomPermission
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate


class CustomPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomPermission
        fields = ['id', 'codename', 'name', 'description', 'category']


class RoleSerializer(serializers.ModelSerializer):
    permission_ids = serializers.PrimaryKeyRelatedField(
        source='permissions',
        queryset=CustomPermission.objects.all(),
        many=True,
        write_only=True,
        required=False
    )
    permissions = CustomPermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'permissions', 'permission_ids', 'created_at']


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
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'phone', 'department', 'position', 'avatar',
            'is_active', 'date_joined', 'roles', 'role_ids',
            'password', 'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        roles = validated_data.pop('roles', [])
        password = validated_data.pop('password', None)
        user = User.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        user.roles.set(roles)
        return user

    def update(self, instance, validated_data):
        roles = validated_data.pop('roles', None)
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()

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
