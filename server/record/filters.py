import django_filters
from .models import ProcessRecord, OAInfo, OAPerson


class ProcessRecordFilter(django_filters.FilterSet):
    # 文本模糊查询
    person_name = django_filters.CharFilter(lookup_expr='icontains')
    unit = django_filters.CharFilter(lookup_expr='icontains')
    department = django_filters.CharFilter(lookup_expr='icontains')
    oa_link_info = django_filters.CharFilter(lookup_expr='icontains')

    # 加密字段：仅支持精确匹配（无法模糊）
    phone_number = django_filters.CharFilter(method='filter_phone_number')
    id_number = django_filters.CharFilter(method='filter_id_number')

    # 下拉单选
    person_type = django_filters.ChoiceFilter(choices=ProcessRecord.PERSON_TYPE_CHOICES)
    id_type = django_filters.ChoiceFilter(choices=ProcessRecord.ID_TYPE_CHOICES)
    card_status = django_filters.ChoiceFilter(choices=ProcessRecord.CARD_STATUS_CHOICES)
    pledged_status = django_filters.ChoiceFilter(choices=ProcessRecord.PLEDGED_STATUS_CHOICES)

    # 状态：支持多选
    registration_status = django_filters.MultipleChoiceFilter(choices=ProcessRecord.STATUS_CHOICES)

    # 是否后补：映射到 is_emergency
    is_emergency = django_filters.CharFilter(method='filter_is_emergency')

    # 是否异常
    is_normal = django_filters.CharFilter(method='filter_is_normal')

    # 时间范围：申请进入/离开时间
    apply_enter_time_after = django_filters.DateTimeFilter(field_name='apply_enter_time', lookup_expr='gte')
    apply_enter_time_before = django_filters.DateTimeFilter(field_name='apply_enter_time', lookup_expr='lte')
    apply_leave_time_after = django_filters.DateTimeFilter(field_name='apply_leave_time', lookup_expr='gte')
    apply_leave_time_before = django_filters.DateTimeFilter(field_name='apply_leave_time', lookup_expr='lte')

    # 时间范围：实际入场/离场
    entered_time_after = django_filters.DateTimeFilter(field_name='entered_time', lookup_expr='gte')
    entered_time_before = django_filters.DateTimeFilter(field_name='entered_time', lookup_expr='lte')
    exited_time_after = django_filters.DateTimeFilter(field_name='exited_time', lookup_expr='gte')
    exited_time_before = django_filters.DateTimeFilter(field_name='exited_time', lookup_expr='lte')

    # 申请时间 applicant_time
    applicant_time_after = django_filters.DateTimeFilter(field_name='applicant_time', lookup_expr='gte')
    applicant_time_before = django_filters.DateTimeFilter(field_name='applicant_time', lookup_expr='lte')

    class Meta:
        model = ProcessRecord
        fields = []  # 所有字段通过显式定义控制

    def filter_phone_number(self, queryset, name, value):
        try:
            return queryset.filter(phone_number=value)
        except Exception:
            return queryset.none()

    def filter_id_number(self, queryset, name, value):
        try:
            return queryset.filter(id_number=value)
        except Exception:
            return queryset.none()

    def filter_is_emergency(self, queryset, name, value):
        if value == '1':
            return queryset.filter(is_emergency=True)
        elif value == '2':
            return queryset.filter(is_emergency=False)
        return queryset

    def filter_is_normal(self, queryset, name, value):
        if value == '1':
            return queryset.filter(is_normal=True)
        elif value == '2':
            return queryset.filter(is_normal=False)
        return queryset


class OAPersonFilter(django_filters.FilterSet):
    person_name = django_filters.CharFilter(lookup_expr='icontains')
    unit = django_filters.CharFilter(lookup_expr='icontains')
    department = django_filters.CharFilter(lookup_expr='icontains')
    person_type = django_filters.ChoiceFilter(choices=OAPerson._meta.get_field('person_type').choices)
    id_type = django_filters.ChoiceFilter(choices=OAPerson._meta.get_field('id_type').choices)

    # 加密字段精确匹配（不支持模糊）
    phone_number = django_filters.CharFilter(method='filter_phone_number')
    id_number = django_filters.CharFilter(method='filter_id_number')

    class Meta:
        model = OAPerson
        fields = []

    def filter_phone_number(self, queryset, name, value):
        try:
            return queryset.filter(phone_number=value)
        except Exception:
            return queryset.none()

    def filter_id_number(self, queryset, name, value):
        try:
            return queryset.filter(id_number=value)
        except Exception:
            return queryset.none()


class OAInfoFilter(django_filters.FilterSet):
    applicant = django_filters.CharFilter(field_name='applicant', lookup_expr='icontains')
    oa_link_info = django_filters.CharFilter(field_name='oa_link_info', lookup_expr='icontains')
    apply_enter_time_after = django_filters.DateTimeFilter(field_name='apply_enter_time', lookup_expr='gte')
    apply_enter_time_before = django_filters.DateTimeFilter(field_name='apply_enter_time', lookup_expr='lte')
    apply_leave_time_after = django_filters.DateTimeFilter(field_name='apply_leave_time', lookup_expr='gte')
    apply_leave_time_before = django_filters.DateTimeFilter(field_name='apply_leave_time', lookup_expr='lte')
    create_time_after = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    create_time_before = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')

    class Meta:
        model = OAInfo
        fields = []
