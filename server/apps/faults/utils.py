import datetime
from apps.faults.models import Event


def build_fault_context(event: Event) -> dict:
    """
    将 Event 及其关联设备、部件信息聚合成一个扁平字典，供规则/AI 使用
    """
    # 基础字段
    data = {
        "mal_id": event.mal_id,
        "first_level": event.first_level or "",
        "subdivision": event.subdivision or "",  # 二级
        "third_level": event.third_level or "",
        "fourth_level": event.fourth_level or "",
        "mal_reason": event.mal_reason or "",
        "description": event.description or "",
        "solution": event.solution or "",
        "level": event.level,
        "category": event.category,
    }

    # 尝试获取第一个设备信息（多设备可取主设备或拼接）
    device_info = event.device_info.first()
    if device_info:
        data.update({
            "equipment_ip": device_info.equipment_ip,
            "device_model": device_info.device_model,
            "brand": device_info.brand,
            "component_name": device_info.component_name,
            "component_brand": device_info.component_brand,
            "component_specification": device_info.component_specification,
            "slot": device_info.slot,
            # 如果有温度等指标，可从 machine_info 或 notes 解析（此处略）
        })

    return data


def get_error_time(error_time_list):
    for i in error_time_list:
        for j in error_time_list:
            if i['start_time'] < j['start_time'] < i['end_time']:
                i['end_time'] = j['end_time']
                j['start_time'], j['end_time'] = 0, 0
    all_start_time = sum([i['start_time'] for i in error_time_list])
    all_end_time = sum([i['end_time'] for i in error_time_list])
    all_error_time = all_end_time - all_start_time
    return all_error_time


def get_last_time(query_type, time_range):
    now = datetime.datetime.now()
    dt = datetime.datetime.fromtimestamp(time_range[1])
    if query_type == 'week':
        return int(time_range[0]) - 86400 * 7, int(time_range[0])
    elif query_type == 'month':
        if dt.month == 1:
            start = now.replace(year=now.year - 1, month=12, day=1)
        else:
            start = now.replace(month=now.month - 1, day=1)
        return int(start.timestamp()), time_range[0]
    elif query_type == 'year':
        return now.replace(year=now.year - 1, month=1, day=1).timestamp(), time_range[0]

