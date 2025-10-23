from django.urls import path, include
from basic.views import EmployeeViewSet, OrgViewSet, RoleViewSet, RoleConnEmployeeViewSet, RoleConnOrgViewSet, \
    MenuViewSet, RoleConnMenuViewSet, PermissionViewSet, RoleConnPermissionViewSet, MenuConnPermissionViewSet, \
    SignViewSet, SignAPIsViewSet, OperateLogViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('employee', EmployeeViewSet, 'employee')
router.register('org', OrgViewSet, 'org')
router.register('role', RoleViewSet, 'role')
router.register('role-conn-employee', RoleConnEmployeeViewSet, 'role-conn-employee')
router.register('role-conn-org', RoleConnOrgViewSet, 'role-conn-org')
router.register('menu', MenuViewSet, 'menu')
router.register('role-conn-menu', RoleConnMenuViewSet, 'role-conn-menu')
router.register('permission', PermissionViewSet, 'permission')
router.register('role-conn-permission', RoleConnPermissionViewSet, 'role-conn-permission')
router.register('menu-conn-permission', MenuConnPermissionViewSet, 'menu-conn-permission')
router.register('sign', SignViewSet, 'sign')
router.register('sign-apis', SignAPIsViewSet, 'sign-apis')
# router.register('audit', AuditViewSet, 'audit')
router.register('operate-log', OperateLogViewSet, 'operate-log')

urlpatterns = [
    path("", include(router.urls)),
]



