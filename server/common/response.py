
from rest_framework.response import Response as DRFResponse
from . import status as custom_status   # 上面定义的 status
from rest_framework import status as http_status   # DRF HTTP status


class APIResponse(DRFResponse):
    """
    统一的 API 响应封装
    格式: { "code": 0, "msg": "success", "data": {} }
    """

    def __init__(
        self,
        data=None,
        code=custom_status.CustomStatus.SUCCESS,
        msg=None,
        status=http_status.HTTP_200_OK,
        headers=None,
        **kwargs
    ):
        """
        :param data: 响应数据
        :param code: 业务状态码
        :param msg: 业务消息（若为空则根据 code 自动获取）
        :param status: HTTP 状态码
        :param headers: 响应头
        """
        msg = msg or custom_status.CustomStatus.get_msg(code)

        # 构造统一响应体
        response_data = {
            "code": code,
            "msg": msg,
            "data": data,
        }

        super().__init__(data=response_data, status=status, headers=headers, **kwargs)
