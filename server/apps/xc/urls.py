from django.urls import path, include
from apps.xc.views import ProductViewSet, ApplicationViewSet, ProjectViewSet, VersionViewSet, AppViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('product', ProductViewSet, 'product')  # 产品线
router.register('application', ApplicationViewSet, 'application')  # 应用
router.register('project', ProjectViewSet, 'project')  # 项目
router.register('version', VersionViewSet, 'version')  # 版本
router.register('app', AppViewSet, 'app')  # 主要维护第三方应用信息+cmdb应用

urlpatterns = [
    path("", include(router.urls)),
]
