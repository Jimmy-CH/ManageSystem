from django.http import JsonResponse


def custom_response(data=None, code=200, message="成功", success=True, http_status=200, **kwargs):
    """
    自定义 JSON 响应封装
    :param data: 返回的数据
    :param code: 业务状态码（自定义，如 0, 4002, 5001）
    :param message: 提示信息
    :param success: 是否成功（可选）
    :param http_status: HTTP 状态码（必须是 100-599 的整数，默认 200）
    :param kwargs: 其他字段
    :return: JsonResponse
    """
    # 安全校验：确保 http_status 合法
    if not isinstance(http_status, int) or not (100 <= http_status <= 599):
        http_status = 200 if success else 500

    response_data = {
        "code": code,
        "message": message,
        "success": success,
        "data": data,
    }
    response_data.update(kwargs)

    return JsonResponse(response_data, status=http_status, json_dumps_params={'ensure_ascii': False})
