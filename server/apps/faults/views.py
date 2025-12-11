import time
import json
import datetime
import pandas as pd
from collections import Counter

from django.db.models import Q, Count, Sum, Avg, Value, Case, When, CharField, Min, FloatField
from django.http import JsonResponse
from rest_framework import viewsets
from .models import (
    EventCategory, EventComponentInfo, Event,
    EventDeviceInfo, EventHandleProcess,
    EventTimeEffective, EventTimeSpecial
)
from .serializers import (
    EventCategorySerializer, EventComponentInfoSerializer,
    EventSerializer, EventTimeEffectiveSerializer,
    EventTimeSpecialSerializer
)
from .filters import (
    EventFilter, EventCategoryFilter, EventComponentInfoFilter,
    EventTimeEffectiveFilter, EventTimeSpecialFilter
)
from .constants import LEVEL_MAP
from .utils import get_last_time, get_error_time


class EventCategoryViewSet(viewsets.ModelViewSet):
    queryset = EventCategory.objects.all()
    serializer_class = EventCategorySerializer
    filterset_class = EventCategoryFilter
    search_fields = ['name']
    ordering_fields = ['update_time', 'depth']


class EventComponentInfoViewSet(viewsets.ModelViewSet):
    queryset = EventComponentInfo.objects.select_related('event_sub')
    serializer_class = EventComponentInfoSerializer
    filterset_class = EventComponentInfoFilter
    search_fields = ['component_name', 'component_brand', 'component_model']


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.prefetch_related(
        'device_info', 'event_handle_process'
    ).select_related().order_by('-update_time')
    serializer_class = EventSerializer
    filterset_class = EventFilter
    search_fields = ['mal_id', 'registrant', 'handler', 'description']
    ordering_fields = ['start_time', 'duration', 'update_time']


class EventTimeEffectiveViewSet(viewsets.ModelViewSet):
    queryset = EventTimeEffective.objects.all()
    serializer_class = EventTimeEffectiveSerializer
    filterset_class = EventTimeEffectiveFilter
    ordering_fields = ['update_time']


class EventTimeSpecialViewSet(viewsets.ModelViewSet):
    queryset = EventTimeSpecial.objects.all()
    serializer_class = EventTimeSpecialSerializer
    filterset_class = EventTimeSpecialFilter
    ordering_fields = ['update_time']


# 数据统计接口
def fault_statistics_data(request):
    """
    故障事件统计页面接口，包含：
     1.故障总数、故障时长、稳定率、一次解决成功率
     2.故障类型（一级、三级分类）饼图数据、故障级别饼图数据
     3.故障分类表格数据
    """
    category = request.GET.get('category')
    first_level = request.GET.get('first_level')
    query_type = request.GET.get('query_type', 'week')

    # 解析时间范围
    time_range_str = request.GET.get('time_range')
    if time_range_str:
        time_range = [int(t) for t in time_range_str.split(',')]
    else:
        now = int(time.time())
        time_range = [now - 86400 * 7, now]

    last_time_range = get_last_time(query_type, time_range)

    # 构建当前周期 QuerySet
    base_q = Q(start_time__gte=time_range[0]) & Q(start_time__lt=time_range[1]) & ~Q(mal_result__in=[4, 5])
    if category:
        base_q &= Q(category=category)
    if first_level:
        base_q &= Q(first_level=first_level)

    current_qs = Event.objects.filter(base_q)

    if not current_qs.exists():
        return JsonResponse({}, safe=False)

    # 获取当前周期的所有事件数据
    current_events = list(current_qs.values(
        'id', 'first_level', 'third_level', 'level', 'mal_result',
        'start_time', 'end_time', 'duration', 'is_overtime', 'mal_id',
        'child_event', 'related_event'
    ))

    # 上一周期 QuerySet
    last_q = Q(start_time__gte=last_time_range[0]) & Q(start_time__lt=last_time_range[1]) & ~Q(mal_result__in=[4, 5])
    if category:
        last_q &= Q(category=category)
    if first_level:
        last_q &= Q(first_level=first_level)
    last_qs = Event.objects.filter(last_q).values(
        'id', 'mal_result', 'level', 'start_time', 'end_time'
    )

    # 当前周期指标
    all_count = len(current_events)
    finished_events = [e for e in current_events if e['mal_result'] == 3]
    finished_count = len(finished_events)
    unfinished_count = all_count - finished_count

    error_time_list = [e for e in finished_events if e['level'] != 5]
    all_error_time = get_error_time(error_time_list)
    no_error_rate = 1 - all_error_time / (time_range[1] - time_range[0]) if (time_range[1] - time_range[0]) > 0 else 0

    first_deal = sum(
        1 for e in current_events
        if not (e['child_event'] or '').strip() and not (e['related_event'] or '').strip()
    )

    # 上一周期指标
    last_all_count = len(last_qs)
    last_finished_events = [e for e in last_qs if e['mal_result'] == 3]
    last_finished_count = len(last_finished_events)
    last_unfinished_count = last_all_count - last_finished_count

    last_error_time_list = [e for e in last_finished_events if e['level'] != 5]
    last_all_error_time = get_error_time(last_error_time_list)
    last_no_error_rate = 1 - last_all_error_time / (last_time_range[1] - last_time_range[0]) if (
                last_time_range[1] - last_time_range[0]) > 0 else 0

    last_first_deal = sum(
        1 for e in last_qs
        if not (e.get('child_event') or '').strip() and not (e.get('related_event') or '').strip()
    )

    # 饼图数据
    third_levels = [e['third_level'] for e in current_events]
    first_levels = [e['first_level'] for e in current_events]
    pie_option_subdivision = [{'name': k, 'value': v} for k, v in Counter(third_levels).items()]
    pie_option_first_level = [{'name': k, 'value': v} for k, v in Counter(first_levels).items()]

    level_counts = Counter(e['level'] for e in current_events)
    pie_option_level = [{'name': LEVEL_MAP.get(lv, f"未知({lv})"), 'value': cnt} for lv, cnt in level_counts.items()]

    # 表格数据
    df = pd.DataFrame(current_events)

    df['duration'] = (df['duration'].fillna(0) * 60).astype(int)  # 转换为秒
    # 聚合1: sum/avg duration
    agg1 = df.groupby('third_level').agg(
        sum_duration=('duration', 'sum'),
        avg_duration=('duration', 'mean'),
        all_count=('id', 'count')
    ).reset_index()
    # 聚合2: unfinished (mal_result=1,2)
    agg2 = df[df['mal_result'].isin([1, 2])].groupby('third_level').size().rename('unfinished_count')
    # 聚合3: finished (mal_result=3)
    agg3 = df[df['mal_result'] == 3].groupby('third_level').size().rename('finished_count')
    # 聚合4: overtime
    agg4 = df.groupby('third_level')['is_overtime'].sum().rename('overtime_count')
    # 聚合5: max duration per third_level
    idx_max = df.groupby('third_level')['duration'].idxmax()
    max_df = df.loc[idx_max, ['third_level', 'duration', 'mal_id']].set_index('third_level')
    # 聚合6: level distribution
    level_pivot = df.pivot_table(
        index='third_level', columns='level', values='id',
        aggfunc='count', fill_value=0
    )
    # 合并
    table_df = agg1.set_index('third_level')
    for agg in [agg2, agg3, agg4]:
        table_df = table_df.join(agg, how='left')
    table_df = table_df.fillna(0)
    table_df = table_df.join(level_pivot, how='left').fillna(0)
    # 转为字典列表
    table_data = []
    for third_level, row in table_df.iterrows():
        item = {
            'subdivision': third_level,
            'sum_duration': int(row['sum_duration']),          # 秒，整数
            'avg_duration': int(row['avg_duration']) if not pd.isna(row['avg_duration']) else 0,
            'unfinished_count': int(row['unfinished_count']),
            'finished_count': int(row['finished_count']),
            'all_count': int(row['all_count']),
            'overtime_count': int(row['overtime_count']),
            'max_duration': int(max_df.loc[third_level, 'duration']) if third_level in max_df.index else 0,
            'max_mal_id': str(max_df.loc[third_level, 'mal_id']) if third_level in max_df.index else '',
        }
        # 只添加非零的级别字段
        for lv in [1, 2, 3, 4, 5]:
            count = int(row.get(lv, 0))
            if count > 0:
                item[LEVEL_MAP[lv]] = count
        # 计算占比
        item['max_duration_per'] = round(
            (item['max_duration'] / item['sum_duration']) * 100, 2
        ) if item['sum_duration'] > 0 else 0
        table_data.append(item)

    # 本月总数
    today = datetime.date.today()
    month_start = today.replace(day=1)
    month_start_ts = int(time.mktime(month_start.timetuple()))
    this_month_count = Event.objects.filter(
        ~Q(mal_result=4),
        start_time__gte=month_start_ts,
        start_time__lt=int(time.time())
    ).count()

    # 返回结果
    resp_data = {
        'all_count': all_count,
        'last_all_count': last_all_count,
        'finished_count': finished_count,
        'last_finished_count': last_finished_count,
        'unfinished_count': unfinished_count,
        'last_unfinished_count': last_unfinished_count,
        'all_error_time': all_error_time,
        'last_all_error_time': last_all_error_time,
        'no_error_rate': no_error_rate,
        'last_no_error_rate': last_no_error_rate,
        'this_month_count': this_month_count,
        'pie_option_subdivision': pie_option_subdivision,
        'pie_option_first_level': pie_option_first_level,
        'pie_option_level': pie_option_level,
        'table_data': table_data,
        'first_deal_per': round((first_deal / all_count) * 100, 2) if all_count else 0,
        'last_first_deal_per': round((last_first_deal / last_all_count) * 100, 2) if last_all_count else 0,
    }

    return JsonResponse(resp_data, safe=False)


def fault_statistics_device_data(request):
    """
    故障事件统计页面接口：设备型号饼图数据
    """
    category = request.GET.get('category', '1')  # 原代码传入的是字符串 '1'，但 filter 时会转为 int
    time_range = request.GET.get('time_range')

    if time_range:
        time_range = [int(i) for i in time_range.split(',')]
    else:
        now = int(time.time())
        time_range = [now - 86400 * 7, now]

    # 构建事件查询集
    event_filter = (Q(category=category) &
                    Q(start_time__gte=time_range[0]) &
                    Q(start_time__lt=time_range[1]) &
                    ~Q(mal_result__in=[4, 5]))

    first_level = request.GET.get('first_level')
    if first_level:
        event_filter &= Q(first_level=first_level)

    event_ids = Event.objects.filter(event_filter).values_list('id', flat=True)

    # 查询关联的设备信息，并处理空值为 '无'
    device_info_qs = EventDeviceInfo.objects.filter(
        event_id__in=event_ids
    ).annotate(
        brand_cleaned=Case(
            When(brand__isnull=True, then=Value('无')),
            When(brand='', then=Value('无')),
            default='brand',
            output_field=CharField()
        ),
        model_cleaned=Case(
            When(device_model__isnull=True, then=Value('无')),
            When(device_model='', then=Value('无')),
            default='device_model',
            output_field=CharField()
        )
    )

    # 聚合计数
    brand_counts = device_info_qs.values('brand_cleaned').annotate(count=Count('brand_cleaned'))
    model_counts = device_info_qs.values('model_cleaned').annotate(count=Count('model_cleaned'))

    # 转换为前端所需格式
    brands = [{'name': item['brand_cleaned'], 'value': item['count']} for item in brand_counts]
    device_models = [{'name': item['model_cleaned'], 'value': item['count']} for item in model_counts]

    return JsonResponse({'brands': brands, 'device_models': device_models}, safe=False)


def fault_statistics_maintenance_data(request):
    """
    故障事件统计页面接口：维保商饼图数据
    """
    # 解析时间范围，默认最近7天
    time_range_str = request.GET.get('time_time') or request.GET.get('time_range')
    if time_range_str:
        try:
            time_range = [int(t) for t in time_range_str.split(',')]
        except (ValueError, TypeError):
            time_range = [int(time.time()) - 86400 * 7, int(time.time())]
    else:
        time_range = [int(time.time()) - 86400 * 7, int(time.time())]

    start_time, end_time = time_range

    # 构建基础查询条件
    query_filters = Q(
        start_time__gte=start_time,
        start_time__lt=end_time,
        solution_type=2,
    ) & ~Q(mal_result__in=[4, 5])

    first_level = request.GET.get('first_level')
    if first_level:
        query_filters &= Q(first_level=first_level)

    # 执行聚合查询
    maintenance_counts = (
        Event.objects
        .filter(query_filters)
        .values('maintenance')
        .annotate(count=Count('maintenance'))
        .values('maintenance', 'count')
    )

    # 转换为前端所需格式
    resp = [
        {"name": item['maintenance'], "value": item["count"]}
        for item in maintenance_counts
        if item['maintenance']
    ]

    return JsonResponse(resp, safe=False)


def fault_statistics_level_data(request):
    """
    故障事件统计页面接口：根据故障等级统计故障数量（堆叠柱状图）
    """

    category = request.GET.get('category', '1')
    time_range_param = request.GET.get('time_range')
    first_level = request.GET.get('first_level')

    if time_range_param:
        start_ts, end_ts = map(int, time_range_param.split(','))
    else:
        end_ts = int(time.time())
        start_ts = end_ts - 86400 * 7

    if end_ts <= start_ts:
        end_ts = start_ts + 86400

    duration = end_ts - start_ts

    # 确定间隔（单位：天）
    if duration <= 86400 * 10:
        interval_days = 1
    elif duration <= 86400 * 33:
        interval_days = 3
    elif duration <= 86400 * 99:
        interval_days = 7
    else:
        interval_days = 30

    queryset = Event.objects.filter(
        start_time__range=(start_ts, end_ts),
        category=category
    ).exclude(mal_result__in=[4, 5])

    if first_level:
        queryset = queryset.filter(first_level=first_level)

    events = list(queryset.values('start_time', 'level'))

    # 生成所有时间桶（按北京时间 00:00 对齐）
    def ts_to_local_date_str(ts):
        return time.strftime('%m-%d', time.localtime(ts))

    # 找到全局最早和最晚日期（按本地日）
    min_date = datetime.datetime.fromtimestamp(start_ts).date()
    max_date = datetime.datetime.fromtimestamp(end_ts).date()

    # 生成所有桶的起始日期（按 interval_days 对齐）
    bucket_dates = []
    current = min_date
    # 先对齐到 interval 起点
    days_offset = (current - datetime.datetime(1970, 1, 1).date()).days
    aligned_offset = (days_offset // interval_days) * interval_days
    current = datetime.datetime(1970, 1, 1).date() + datetime.timedelta(days=aligned_offset)

    while current <= max_date:
        bucket_dates.append(current)
        current += datetime.timedelta(days=interval_days)

    # 转为时间戳范围：每个桶 [start_ts, end_ts)
    buckets = []
    day_list = []
    for i, date in enumerate(bucket_dates):
        start_of_day = int(datetime.datetime.combine(date, datetime.datetime.min.time()).timestamp())
        end_of_day = start_of_day + 86400 * interval_days
        day_str = ts_to_local_date_str(start_of_day)
        buckets.append((start_of_day, end_of_day))
        day_list.append(day_str)
    level_map = {5: "无影响", 1: "轻微", 2: "一般", 3: "严重", 4: "灾难"}
    res = {day: {level: 0 for level in level_map} for day in day_list}
    for event in events:
        ts = event['start_time']
        level = event['level']
        # 找到所属桶
        assigned = False
        for i, (b_start, b_end) in enumerate(buckets):
            if b_start <= ts < b_end:
                day_key = day_list[i]
                res[day_key][level] += 1
                assigned = True
                break
    data_dict = {}
    for level, label in level_map.items():
        data_dict[label] = [res[day][level] or None for day in day_list]

    # 构建 series
    series = []
    for label, data in data_dict.items():
        series.append({
            'name': label,
            'type': 'bar',
            'stack': '总量',
            'label': {'show': True, 'position': 'insideRight'},
            'data': data
        })

    return JsonResponse({'day_list': day_list, 'series': series}, safe=False)


def fault_statistics_impact_project_data(request):
    """
     故障事件统计页面接口：影响项目表格数据
    """
    time_range = request.GET.get('time_range')
    first_level = request.GET.get('first_level')
    category = request.GET.get('category', '1')

    if time_range:
        start_ts, end_ts = map(int, time_range.split(','))
    else:
        end_ts = int(time.time())
        start_ts = end_ts - 86400 * 7

    queryset = Event.objects.filter(
        start_time__range=(start_ts, end_ts),
        category=category
    ).exclude(mal_result__in=[4, 5])

    if first_level:
        queryset = queryset.filter(first_level=first_level)

    events = list(queryset)
    if not events:
        return JsonResponse([], safe=False)

    # 提取数据，安全处理 impact_pro
    data = []
    for event in events:
        impact_pro = event.impact_pro
        # 确保 impact_pro 是非空列表
        if not isinstance(impact_pro, (list, tuple)) or len(impact_pro) == 0:
            continue
        primary_project = impact_pro[0]
        data.append({
            'project': primary_project,
            'malfunction_id': event.id,
            'level': event.level,
            'mal_result': event.mal_result,
            'is_overtime': event.is_overtime,
            'mal_id': event.mal_id,
            'duration': event.duration  # 假设单位：小时
        })

    if not data:
        return JsonResponse([], safe=False)

    df = pd.DataFrame(data)

    # 去重：同一项目 + 同一故障只保留一条
    df.drop_duplicates(subset=['project', 'malfunction_id'], keep='first', inplace=True)
    if df.empty:
        return JsonResponse([], safe=False)

    # 按 project 分组
    grouped = df.groupby('project')

    result = []
    for project, group in grouped:
        # 基础计数
        all_count = len(group)
        finished_count = int((group['mal_result'] == 3).sum())
        unfinished_count = int(group['mal_result'].isin([1, 2]).sum())
        overtime_count = int((group['is_overtime'] == 1).sum())

        # 持续时间（单位：小时 → 输出为分钟）
        durations = group['duration']
        total_duration_h = float(durations.sum())
        avg_duration_h = float(durations.mean()) if not pd.isna(durations.mean()) else 0.0

        sum_duration_min = round(total_duration_h * 60, 2)
        avg_duration_min = round(avg_duration_h * 60, 2)

        # 最长持续时间事件
        max_idx = group['duration'].idxmax()
        max_row = group.loc[max_idx]
        max_duration_h = float(max_row['duration'])
        max_duration_min = round(max_duration_h * 60, 2)
        mal_id_val = max_row['mal_id']
        max_mal_id = str(mal_id_val) if pd.notna(mal_id_val) else ""
        max_duration_per = round((max_duration_h / total_duration_h * 100), 2) if total_duration_h > 0 else 0.0

        # 按等级统计
        level_counts = group['level'].value_counts().to_dict()
        level_stats = {
            LEVEL_MAP[level]: int(level_counts.get(level, 0))
            for level in LEVEL_MAP
        }

        # 构建最终项（所有值转为原生 Python 类型）
        item = {
            'project': project,
            'all_count': all_count,
            'finished_count': finished_count,
            'unfinished_count': unfinished_count,
            'sum_duration': sum_duration_min,
            'avg_duration': avg_duration_min,
            'overtime_count': overtime_count,
            'max_mal_id': max_mal_id,
            'max_duration': max_duration_min,
            'max_duration_per': max_duration_per,
            **level_stats
        }

        result.append(item)

    return JsonResponse(result, safe=False)


def fault_statistics_category_trend_data(request):
    """
    故障事件统计页面接口：故障分类表格中趋势图数据
    """
    subdivision = request.GET.get('subdivision')
    if not subdivision:
        return JsonResponse({'error': 'need subdivision'}, safe=False)

    # 解析时间范围（前端传毫秒，转为秒）
    time_range_str = request.GET.get('time_range')
    if time_range_str:
        try:
            time_range = [int(ts) // 1000 for ts in time_range_str.split(',')]
        except (ValueError, TypeError):
            now = int(time.time())
            time_range = [now - 86400 * 30, now]
    else:
        now = int(time.time())
        time_range = [now - 86400 * 30, now]

    query_filters = {
        'start_time__gte': time_range[0],
        'start_time__lt': time_range[1],
        'third_level': subdivision,
    }

    first_level = request.GET.get('first_level')
    if first_level:
        query_filters['first_level'] = first_level

    events = Event.objects.filter(**query_filters).values_list('start_time', flat=True)
    # 生成完整日期序列（北京时间自然日）
    start_dt = datetime.datetime.fromtimestamp(time_range[0])  # 转为本地 datetime
    end_dt = datetime.datetime.fromtimestamp(time_range[1])
    # 对齐到起始日的 00:00:00
    start_day = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    end_day = end_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    if end_dt > end_day:
        end_day += datetime.timedelta(days=1)

    day_list = []
    current = start_day
    while current < end_day:
        day_list.append(int(current.timestamp()))  # 转回时间戳（秒）
        current += datetime.timedelta(days=1)
    # 按自然日分组计数
    from collections import defaultdict
    daily_count = defaultdict(int)

    for ts in events:
        dt = datetime.datetime.fromtimestamp(ts)
        day_start = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        day_ts = int(day_start.timestamp())
        daily_count[day_ts] += 1

    # 构造完整数据序列（缺失日补 0）
    data = []
    for day_ts in day_list:
        count = daily_count.get(day_ts, 0)
        data.append([day_ts * 1000, count])  # 转为毫秒

    series = [{
        "name": subdivision,
        "type": "line",
        "symbol": "none",
        "stack": "vistors",
        "areaStyle": {},
        "data": data
    }]

    return JsonResponse(series, safe=False)


def fault_statistics_device_unit_data(request):
    """
    故障与事件统计页面接口：故障部件占比饼图数据
    """
    time_range = request.GET.get('time_range')
    if time_range:
        time_range = [int(ts) for ts in time_range.split(',')]
    else:
        now = int(time.time())
        time_range = [now - 86400 * 7, now]

    category = request.GET.get('category', '1')

    # 构建查询条件（全部通过 event__ 关联到 Event 模型）
    query_filters = Q(
        event__start_time__gte=time_range[0],
        event__start_time__lt=time_range[1],
        event__category=category,
    ) & ~Q(event__mal_result__in=[4, 5])

    first_level = request.GET.get('first_level')
    if first_level:
        query_filters &= Q(event__first_level=first_level)

    queryset = EventDeviceInfo.objects.filter(query_filters)

    total = queryset.count()
    if total == 0:
        return JsonResponse([], safe=False)

    component_stats = queryset.values('component_name').annotate(
        count=Count('id')
    ).values('component_name', 'count')

    result = [
        {
            'name': item['component_name'] if item['component_name'] is not None else None,
            'value': item['count'],
            'per': round(item['count'] / total, 10)
        }
        for item in component_stats
    ]

    return JsonResponse(result, safe=False)


def fault_statistics_annual_data(request):
    """
    故障事件统计页面接口:年度故障次数统计
    统计年度故障次数大于等于2次的设备，机房使用设备名称，主机使用设备型号
    """
    first_level = request.GET.get('first_level')
    if first_level and first_level != '主机存储组':
        return JsonResponse([], safe=False)

    today = datetime.date.today()
    year_start = today.replace(month=1, day=1)
    start_timestamp = int(time.mktime(year_start.timetuple()))
    end_timestamp = int(time.time())

    data_center = (
        EventDeviceInfo.objects
        .filter(
            Q(event__category=1) &
            Q(event__first_level="主机存储组") &
            Q(event__subdivision="机房") &
            Q(event__start_time__range=(start_timestamp, end_timestamp)) &
            ~Q(event__mal_result__in=[4, 5])
        )
        .values('device_name')
        .annotate(count=Count('id'))
        .filter(count__gt=1)
    )

    result = [
        {'name': item['device_name'], 'value': item['count']}
        for item in data_center
    ]

    host = (
        EventDeviceInfo.objects
        .filter(
            Q(event__category=1) &
            Q(event__first_level="主机存储组") &
            Q(event__subdivision="主机") &
            Q(event__start_time__range=(start_timestamp, end_timestamp)) &
            ~Q(event__mal_result__in=[4, 5])
        )
        .values('device_model')
        .annotate(count=Count('id'))
        .filter(count__gt=1)
    )

    for i in host:
        result.append({'name': i['device_model'], 'value': i['count']})

    return JsonResponse(result, safe=False)


# 服务商统计页面接口
def maintenance_statistics_data(request):
    """
    服务商统计页面接口: 服务商统计基本数据
    """
    time_range = request.GET.get('time_range')
    query_type = request.GET.get('query_type', 'week')
    if not all([time_range, query_type]):
        return JsonResponse({'error': 'need time_range and query_type'}, safe=False)

    try:
        time_range = [int(i) for i in time_range.split(',')]
    except (ValueError, TypeError):
        now = int(time.time())
        time_range = [now - 86400 * 7, now]

    # 构建当前时间段查询
    queryset = Event.objects.filter(
        Q(start_time__range=time_range),
        Q(solution_type=2),
        ~Q(mal_result__in=[4, 5]),
        ~Q(maintenance__isnull=True)
    )
    category = request.GET.get('category')
    if category:
        queryset = queryset.filter(category=category)

    # 获取上一时间段并构建查询
    last_time_range = get_last_time(query_type, time_range=time_range)
    last_m = Event.objects.filter(
        Q(start_time__range=last_time_range),
        Q(solution_type=2),
        ~Q(mal_result__in=[4, 5]),
        ~Q(maintenance__isnull=True)
    )
    if category:
        last_m = last_m.filter(category=category)

    all_count = queryset.count() if queryset.exists() else 0
    last_all_count = last_m.count() if last_m.exists() else 0

    total_duration_agg = queryset.aggregate(total_duration=Sum('maintaince_duration'))
    total_duration = total_duration_agg.get('total_duration', 0)
    total_duration = total_duration / 60 if total_duration else 0

    last_duration_agg = last_m.aggregate(last_duration=Sum('maintaince_duration'))
    last_total_duration = last_duration_agg.get('last_duration', 0)
    last_total_duration = last_total_duration / 60 if last_total_duration else 0

    ret = [
        {"name": i["maintenance"], "value": i["count"]}
        for i in queryset.values('maintenance').annotate(count=Count('id')).values('maintenance', 'count')
    ]

    # 不合格统计
    stack = [
        {"label": item["maintenance"], "value": item["count"]}
        for item in queryset.filter(score__lt=60).values('maintenance').annotate(count=Count('id')).values('maintenance', 'count')
    ]

    return JsonResponse({
        'count': all_count,
        'last_count': last_all_count,
        'total_duration': total_duration,
        'last_total_duration': last_total_duration,
        'maintaince_count_pie': ret,
        'fail_counts': stack
    }, safe=False)


def maintenance_statistics_score_data(request):
    """
    服务商统计页面接口: 服务商评分柱状图数据
    评分逻辑：
      - fail_sum = count of score < 60
      - avg_score =
            mean(score)  if min(score) >= 80
            min(score)   otherwise
    """
    time_range_param = request.GET.get('time_range')
    if time_range_param:
        try:
            time_range = [int(ts) for ts in time_range_param.split(',')]
        except (ValueError, TypeError):
            now = int(time.time())
            time_range = [now - 86400 * 7, now]
    else:
        now = int(time.time())
        time_range = [now - 86400 * 7, now]

    queryset = Event.objects.filter(
        Q(start_time__range=time_range),
        Q(solution_type=2),
        ~Q(mal_result__in=[4, 5]),
        ~Q(maintenance__isnull=True)
    )

    category = request.GET.get('category')
    if category:
        queryset = queryset.filter(category=category)

    if not queryset.exists():
        return JsonResponse([], safe=False)
    # 聚合：min, avg, fail_count
    stats = queryset.values('maintenance').annotate(
        min_score=Min('score'),
        avg_score_raw=Avg('score'),
        fail_sum=Count(
            Case(
                When(score__lt=60, then=1),
                output_field=FloatField()
            )
        )
    ).values('maintenance', 'min_score', 'avg_score_raw', 'fail_sum')

    avg_list = []
    fail_list = []

    for item in stats:
        maint = item['maintenance']
        min_score = item['min_score'] or 0
        avg_raw = item['avg_score_raw'] or 0
        fail_sum = item['fail_sum'] or 0
        # 评分逻辑
        if min_score >= 80:
            final_avg = avg_raw
        else:
            final_avg = min_score
        final_avg = round(final_avg, 2)

        avg_list.append({'label': maint, 'value': final_avg})
        fail_list.append({'label': maint, 'value': fail_sum})

    return JsonResponse({
        "avg_score_stack": avg_list,
        "fail_score_stack": fail_list
    }, safe=False)


def maintenance_statistics_score_table_data(request):
    """
    服务商统计页面接口：服务商评分表格数据
    """

    def extract_score_further_deal(remarks_str):
        """从 JSON 字符串中提取 score_further_deal，失败返回 None"""
        if not remarks_str:
            return None
        try:
            data = json.loads(remarks_str)
            return data.get('score_further_deal')
        except (json.JSONDecodeError, TypeError, AttributeError):
            return None

    time_range_param = request.GET.get('time_range')
    if time_range_param:
        try:
            time_range = [int(ts) for ts in time_range_param.split(',')]
        except (ValueError, TypeError):
            now = int(time.time())
            time_range = [now - 86400 * 7, now]
    else:
        now = int(time.time())
        time_range = [now - 86400 * 7, now]

    queryset = Event.objects.filter(
        Q(start_time__range=time_range),
        Q(solution_type=2),
        ~Q(mal_result__in=[4, 5]),
        ~Q(maintenance__isnull=True)
    )

    category = request.GET.get('category')
    if category:
        queryset = queryset.filter(category=category)

    if not queryset.exists():
        return JsonResponse([], safe=False)

    records = queryset.values(
        'maintenance',
        'maintaince_duration',
        'score',
        'maintaince_status',
        'maintenance_remarks',
        'is_overtime'
    )
    from collections import defaultdict
    # 按 maintenance 分组聚合
    groups = defaultdict(list)
    for rec in records:
        groups[rec['maintenance']].append(rec)

    result = []
    for maint, events in groups.items():
        durations = [e['maintaince_duration'] or 0 for e in events]
        scores = [e['score'] for e in events if e['score'] is not None]
        statuses = [e['maintaince_status'] for e in events]
        overtimes = [e['is_overtime'] for e in events]
        # 解析 score_further_deal
        score_further_list = []
        for e in events:
            val = extract_score_further_deal(e['maintenance_remarks'])
            score_further_list.append(val)
        # 聚合计算
        stats = {
            'maintenance': maint,
            'count': len(events),
            'max_duration': max(durations) / 60 if durations else 0,
            'total': sum(durations) / 60,
        }
        # avg_score: 特殊规则
        if scores:
            min_score = min(scores)
            if min_score >= 80:
                avg_score = round(sum(scores) / len(scores), 2)
            else:
                avg_score = min_score
        else:
            avg_score = 0
        stats['avg_score'] = avg_score
        # 状态计数
        stats['已处理'] = sum(1 for s in statuses if s == 2)
        stats['处理中'] = sum(1 for s in statuses if s == 1)
        stats['未处理'] = sum(1 for s in statuses if s == 0)
        # 无需处理：score_further_deal == False（注意：None 或 True 不算）
        stats['无需处理'] = sum(1 for v in score_further_list if v is False)
        # 超时次数
        stats['超时次数'] = sum(1 for o in overtimes if o == 1)
        result.append(stats)

    return JsonResponse(result, safe=False)
