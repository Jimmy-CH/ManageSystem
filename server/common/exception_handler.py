from rest_framework.views import exception_handler
from django.http import Http404
from django.db import connections
from rest_framework import exceptions
from django.core.exceptions import PermissionDenied

from common import custom_response
from common import CustomStatus

import logging

logger = logging.getLogger('ms')


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


def handler(exc, context):
    # 回滚数据库事务（保留原有逻辑）
    for db in connections.all():
        if db.settings_dict['ATOMIC_REQUESTS'] and db.in_atomic_block:
            db.set_rollback(True)

    if isinstance(exc, exceptions.ValidationError):
        detail = exc.detail

        # 情况1：字段级错误（dict）
        if isinstance(detail, dict):
            # 提取第一个字段的第一个错误信息（用于 msg）
            for field_errors in detail.values():
                if field_errors:
                    msg = str(field_errors[0])
                    break
            else:
                msg = "请求参数错误"
            # data 中保留完整错误结构
            resp = custom_response(code=CustomStatus.VALIDATION_ERROR, msg=msg, data=detail)

        # 情况2：非字典错误（如 list 或 string）
        elif isinstance(detail, list):
            msg = str(detail[0]) if detail else "请求参数错误"
            resp = custom_response(code=CustomStatus.VALIDATION_ERROR, msg=msg, data=detail)
        else:
            msg = str(detail)
            resp = custom_response(code=CustomStatus.VALIDATION_ERROR, msg=msg, data={})

    elif isinstance(exc, PermissionDenied):
        resp = custom_response(code=CustomStatus.PERMISSION_DENIED, msg="无权访问")

    elif isinstance(exc, exceptions.APIException):
        # 处理 DRF 内置 API 异常（如 NotFound, MethodNotAllowed 等）
        resp = custom_response(code=CustomStatus.SERVER_ERROR, msg=str(exc.detail), data=getattr(exc, 'detail', {}))

    elif isinstance(exc, Http404):
        resp = custom_response(code=CustomStatus.NOT_FOUND, msg="请求地址(资源)不存在")

    else:

        logger.error('Unhandled exception', exc_info=exc)
        resp = custom_response(code=CustomStatus.SERVER_ERROR, msg="服务器内部错误")

    return resp
