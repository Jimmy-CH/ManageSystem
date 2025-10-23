from django_filters import FilterSet, CharFilter
from basic.models import Employee, Org

__all__ = ['EmployeeFilter', 'OrgFilter']


class EmployeeFilter(FilterSet):
    # 自定义前端参数名，映射到正确的模型路径
    deptcode = CharFilter(field_name='dept_id', lookup_expr='exact')
    pk_deptdoc = CharFilter(field_name='dept__id', lookup_expr='exact')

    class Meta:
        model = Employee
        fields = {
            'id': ['exact'],
            'psncode': ['exact'],
            'psnname': ['exact'],
            'email': ['exact'],
            'mobile': ['exact'],
        }


class OrgFilter(FilterSet):
    org_name = CharFilter(lookup_expr='icontains')  # 模糊搜索

    class Meta:
        model = Org
        fields = {
            'id': ['exact'],
            'org_code': ['exact'],
        }
