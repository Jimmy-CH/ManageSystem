
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .filters import RoleFilter
from .models import User, Role, CustomPermission
from .serializers import UserSerializer, RoleSerializer, CustomPermissionSerializer, RegisterSerializer, \
    CustomTokenObtainPairSerializer
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from django.db.models import Prefetch
from utils import StandardResponse
import logging
import pandas as pd
from django.http import HttpResponse


logger = logging.getLogger(__name__)


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
        return StandardResponse(data=grouped)

    @action(detail=False, methods=['get'])
    def all(self, request):
        """
        返回所有权限
        """
        queryset = self.get_queryset().values('id', 'name')
        return StandardResponse(data=list(queryset))


class RoleViewSet(viewsets.ModelViewSet):

    queryset = Role.objects.prefetch_related(
        Prefetch(
            'permissions',
            queryset=CustomPermission.objects.only('id', 'name').order_by('name')
        )
    ).all().order_by('name')
    serializer_class = RoleSerializer
    filterset_class = RoleFilter  # ← 启用过滤器
    search_fields = ['name', 'description']
    ordering_fields = ['id', 'name', 'importance', 'created_at']
    ordering = ['id']  # 默认排序

    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        导出角色数据为 Excel
        支持按当前筛选条件导出（过滤、搜索、排序）
        """
        # 1. 获取过滤后的 queryset（应用了 filter + search + ordering）
        queryset = self.filter_queryset(self.get_queryset())

        # 2. 遍历数据，构建导出结构
        data = []
        for role in queryset:
            # 获取权限名称列表，并拼接成字符串
            permission_names = ', '.join([p.name for p in role.permissions.all()])
            data.append({
                'ID': role.id,
                '角色名称': role.name,
                '描述': role.description or '',
                '状态': '启用' if role.status else '禁用',
                '重要程度': role.importance,
                '权限列表': permission_names,
                '创建时间': role.created_at.strftime('%Y-%m-%d %H:%M:%S') if role.created_at else '',
                '更新时间': role.updated_at.strftime('%Y-%m-%d %H:%M:%S') if role.updated_at else '',
            })

        # 3. 用 pandas 生成 Excel
        df = pd.DataFrame(data)

        # 4. 写入内存
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="角色列表.xlsx"'

        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='角色数据')

        return response


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.prefetch_related('roles__permissions').all().order_by('-created_at')
    serializer_class = UserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return StandardResponse(data=serializer.data)


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

            return StandardResponse(code=205, message="登出成功")
        except Exception as e:
            logger.error(f"登出失败，error: {e}")
            return StandardResponse(code=508, message="无效的 token")


class MeView(APIView):
    """
    获取当前用户信息
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return StandardResponse(data=serializer.data)


class CustomPermissionCreateView(APIView):
    permission_classes = [IsAdminUser]  # 仅管理员可访问

    @extend_schema(
        request=CustomPermissionSerializer,
        responses=CustomPermissionSerializer
    )
    def post(self, request):
        # 只有管理员才能创建权限
        serializer = CustomPermissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
