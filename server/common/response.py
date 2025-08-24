# utils/response.py
from django.http import JsonResponse


def custom_response(data=None, code=200, message="成功", success=True, status=None, **kwargs):
    """
    自定义 JSON 响应封装
    :param data: 返回的数据（字典或列表）
    :param code: 业务状态码（自定义）
    :param message: 提示信息
    :param success: 是否成功
    :param status: HTTP 状态码（如 200, 400, 500），默认与 code 相同
    :param kwargs: 其他额外字段
    :return: JsonResponse
    """
    response_data = {
        "code": code,
        "message": message,
        "success": success,
        "data": data,
    }

    # 添加其他自定义字段
    response_data.update(kwargs)

    # 默认 HTTP 状态码
    http_status = status if status is not None else code

    return JsonResponse(response_data, status=http_status, json_dumps_params={'ensure_ascii': False})