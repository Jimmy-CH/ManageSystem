
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User, Role, CustomPermission
from .serializers import UserSerializer, RoleSerializer, CustomPermissionSerializer, RegisterSerializer, \
    CustomTokenObtainPairSerializer
from rest_framework.views import APIView


class CustomPermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    只读权限列表，供前端选择
    """
    queryset = CustomPermission.objects.all().order_by('category', 'name')
    serializer_class = CustomPermissionSerializer
    pagination_class = None  # 权限不多，不分页

    @action(detail=False, methods=['get'])
    def grouped(self, request):
        """
        按 category 分组返回权限
        """
        perms = self.get_queryset()
        grouped = {}
        for p in perms:
            cat = p.category
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append(CustomPermissionSerializer(p).data)
        return Response(grouped)


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.prefetch_related('permissions').all().order_by('name')
    serializer_class = RoleSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.prefetch_related('roles__permissions').all().order_by('-created_at')
    serializer_class = UserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


# 登录、注册、退出保持不变

class RegisterView(APIView):
    """
    用户注册
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        # drf框架捕获异常
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "message": "注册成功",
            "user": UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    """
    用户登录（返回 JWT Token + 用户信息）
    """
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]


class LogoutView(APIView):
    """
    用户登出（将 refresh token 加入黑名单）
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "登出成功"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "无效的 token"}, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    """
    获取当前用户信息
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
