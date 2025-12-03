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


