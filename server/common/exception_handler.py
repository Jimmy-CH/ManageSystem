
from django.http import Http404
from django.db import connections
from rest_framework import exceptions
from django.core.exceptions import PermissionDenied

from common import custom_response
from common import CustomStatus

import logging

logger = logging.getLogger('ms')


def custom_exception_handler(exc, context):
    """全局异常处理器"""
    # 回滚事务
    for db in connections.all():
        if db.settings_dict['ATOMIC_REQUESTS'] and db.in_atomic_block:
            db.set_rollback(True)

    if isinstance(exc, exceptions.ValidationError):
        detail = exc.detail
        if isinstance(detail, dict):
            msg = next(iter(detail.values()))[0] if detail else "请求参数错误"
            resp = custom_response(
                code=CustomStatus.VALIDATION_ERROR,
                message=str(msg),
                data=detail,
                http_status=400  # ← 显式指定
            )
        elif isinstance(detail, list):
            msg = str(detail[0]) if detail else "请求参数错误"
            resp = custom_response(
                code=CustomStatus.VALIDATION_ERROR,
                message=msg,
                data=detail,
                http_status=400
            )
        else:
            resp = custom_response(
                code=CustomStatus.VALIDATION_ERROR,
                message=str(detail),
                data={},
                http_status=400
            )

    elif isinstance(exc, PermissionDenied):
        resp = custom_response(
            code=CustomStatus.PERMISSION_DENIED,
            message="无权访问",
            http_status=403
        )

    elif isinstance(exc, exceptions.AuthenticationFailed):
        resp = custom_response(
            code=CustomStatus.AUTH_FAILED,
            message=str(exc.detail),
            data=getattr(exc, 'detail', {}),
            http_status=401  # ← 关键！认证失败应返回 401
        )

    elif isinstance(exc, exceptions.NotFound):
        resp = custom_response(
            code=CustomStatus.NOT_FOUND,
            message="资源未找到",
            http_status=404
        )

    elif isinstance(exc, exceptions.APIException):
        # 通用 API 异常，尝试保留其 HTTP 状态码
        http_code = getattr(exc, 'status_code', 500)
        if not (100 <= http_code <= 599):
            http_code = 500
        resp = custom_response(
            code=CustomStatus.SERVER_ERROR,
            message=str(exc.detail),
            data=getattr(exc, 'detail', {}),
            http_status=http_code
        )

    elif isinstance(exc, Http404):
        resp = custom_response(
            code=CustomStatus.NOT_FOUND,
            message="请求地址(资源)不存在",
            http_status=404
        )

    else:
        logger.error('Unhandled exception', exc_info=exc)
        resp = custom_response(
            code=CustomStatus.SERVER_ERROR,
            message="服务器内部错误",
            http_status=500  # ← 必须是 500，不是 5001！
        )

    return resp
