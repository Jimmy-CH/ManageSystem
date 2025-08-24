
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from accounts.models import UserProfile, UserRole


# 自定义 Token 返回（含用户和 profile 信息）
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # 获取 profile 信息（可能为空）
        profile = getattr(self.user, 'profile', None)
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'profile': {
                'avatar': profile.avatar.url if profile and profile.avatar else None,
                'address': profile.address if profile else None,
                'phone': profile.phone if profile else None,
                'bio': profile.bio if profile else None,
            } if profile else None,
            'roles': list(UserRole.objects.filter(user=self.user).values_list('role__name', flat=True))
        }
        return data


# 用户注册序列化器（含扩展字段）
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    # 扩展字段
    avatar = serializers.ImageField(required=False)
    address = serializers.CharField(max_length=255, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    bio = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'confirm_password', 'avatar', 'address', 'phone', 'bio')

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "两次密码不一致"})
        return attrs

    def create(self, validated_data):
        # 提取扩展字段
        avatar = validated_data.pop('avatar', None)
        address = validated_data.pop('address', None)
        phone = validated_data.pop('phone', None)
        bio = validated_data.pop('bio', None)

        # 移除 confirm_password
        validated_data.pop('confirm_password')

        # 创建用户
        user = User.objects.create_user(**validated_data)

        # 创建或更新 UserProfile
        profile, created = UserProfile.objects.get_or_create(user=user)
        if avatar:
            profile.avatar = avatar
        if address:
            profile.address = address
        if phone:
            profile.phone = phone
        if bio:
            profile.bio = bio
        profile.save()

        return user


# 用户信息序列化器（用于返回完整用户信息）
class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    roles = serializers.SerializerMethodField()

    def get_roles(self, obj):
        return list(UserRole.objects.filter(user=obj.user).values_list('role__name', flat=True))

    class Meta:
        model = UserProfile
        fields = ('username', 'email', 'avatar', 'address', 'phone', 'bio', 'roles', 'created_at', 'updated_at')
