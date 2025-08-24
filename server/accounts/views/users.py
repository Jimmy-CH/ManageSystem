
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status, viewsets
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.models import UserProfile
from accounts.serializers import MyTokenObtainPairSerializer, UserRegistrationSerializer, UserProfileSerializer
from common import custom_response


# 登录
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# 刷新 Token
class MyTokenRefreshView(TokenRefreshView):
    pass


# 用户注册
class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return custom_response({
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "profile": {
                        "avatar": user.profile.avatar.url if user.profile.avatar else None,
                        "address": user.profile.address,
                        "phone": user.profile.phone,
                        "bio": user.profile.bio,
                    }
                }
            }, status=status.HTTP_201_CREATED)
        return custom_response(message=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 获取用户信息
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.profile  # 通过 OneToOne 获取
        serializer = UserProfileSerializer(profile)
        return custom_response(data=serializer.data)

    # 可选：支持更新用户信息（PUT/PATCH）
    def put(self, request):
        profile = request.user.profile
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return custom_response(data=serializer.data)
        return custom_response(message=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    用户登出视图。
    要求用户已通过认证，并提供其 refresh token 以加入黑名单。
    """
    refresh_token_str = request.data.get("refresh")

    if not refresh_token_str:
        return custom_response(code=400, message='缺少 refresh token', status=status.HTTP_400_BAD_REQUEST)

    try:
        # 1. 验证 refresh token 是否有效（签名、未过期）
        refresh_token = RefreshToken(refresh_token_str)

        # 2. 将 refresh token 加入黑名单
        # 注意：这也会使该 refresh token 派生出的 access token 失效（如果配置了 BLACKLIST_AFTER_ROTATION）
        refresh_token.blacklist()

        return custom_response(
            code=200,
            message='登出成功',
            # data=None, # 如果 custom_response 默认 data=None 可省略
            status=status.HTTP_200_OK
        )

    except TokenError as e:
        # TokenError 是 InvalidToken 的父类，包含了更具体的错误
        # InvalidToken 是更具体的子类
        # 这里捕获 TokenError 可以处理过期、无效签名等情况
        return custom_response(
            code=400,
            message=f'无效或已过期的令牌: {str(e)}',  # 将异常转为字符串
            status=status.HTTP_400_BAD_REQUEST
        )

    except Exception as e:
        # 捕获其他意外错误（如数据库错误）
        # 生产环境中应记录日志而不是只 print
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"登出时发生意外错误: {e}", exc_info=True)

        return custom_response(
            code=500,
            message='服务器内部错误',
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all().order_by('-id')
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]


