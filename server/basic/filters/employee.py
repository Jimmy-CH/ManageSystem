from django_filters import FilterSet, CharFilter
from basic.models import Employee, Org

__all__ = ['EmployeeFilter', 'OrgFilter']


class EmployeeFilter(FilterSet):
    # 仅自定义非 exact 查询
    # （当前都是 exact，所以其实可以全删，但保留结构便于后续扩展）
    class Meta:
        model = Employee
        fields = {
            'id': ['exact'],
            'psncode': ['exact'],
            'psnname': ['exact'],
            'email': ['exact'],
            'mobile': ['exact'],
            'pk_deptdoc': ['exact'],
            'deptcode': ['exact'],
        }


class OrgFilter(FilterSet):
    org_name = CharFilter(lookup_expr='icontains')  # 模糊搜索

    class Meta:
        model = Org
        fields = {
            'id': ['exact'],
            'org_code': ['exact'],
        }
