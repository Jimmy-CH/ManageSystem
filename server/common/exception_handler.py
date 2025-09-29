from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # 调用 DRF 默认异常处理器
    response = exception_handler(exc, context)

    if response is not None:
        original_data = response.data
        message = "请求失败"

        # 处理 ValidationError 等字段错误
        if isinstance(original_data, dict):
            # 遍历字段，取第一个错误
            for field, errors in original_data.items():
                if isinstance(errors, (list, tuple)) and errors:
                    error_msg = str(errors[0])
                    # 字段名人性化（可选：把下划线转中文，或映射）
                    field_name = {
                        'username': '用户名',
                        'phone': '手机号',
                        'department': '部门',
                        'position': '职位',
                        'email': '邮箱',
                    }.get(field, field)
                    message = f"{field_name}: {error_msg}"
                    break
                elif isinstance(errors, str):
                    message = f"{field}: {errors}"
                    break
        elif isinstance(original_data, list) and original_data:
            # 非字段错误（如全局错误）
            message = str(original_data[0])

        # 构造你项目期望的最终响应格式
        response.data = {
            "code": response.status_code,
            "message": message,
            "data": None
        }

    return response
