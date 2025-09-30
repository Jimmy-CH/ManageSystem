from rest_framework.renderers import JSONRenderer


class StandardJSONRenderer(JSONRenderer):
    """
    标准化响应格式：
    {
      "code": 200,
      "message": "成功",
      "data": { ... }
    }
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        # 获取原始响应
        response = renderer_context.get('response') if renderer_context else None
        status_code = response.status_code if response else 200

        # 默认值
        code = status_code
        message = "成功"
        result_data = data

        # 处理错误响应（非 2xx）
        if status_code >= 400:
            message = self._get_error_message(data)
            result_data = None

        # 构造标准响应
        response_data = {
            "code": code,
            "message": message,
            "data": result_data
        }

        return super().render(response_data, accepted_media_type, renderer_context)

    def _get_error_message(self, data):
        """从 DRF 错误响应中提取第一条错误信息"""
        if isinstance(data, dict):
            if 'detail' in data:
                return str(data['detail'])
            for key, value in data.items():
                if isinstance(value, (list, str)):
                    return f"{key}: {value[0] if isinstance(value, list) else value}"
        elif isinstance(data, list) and len(data) > 0:
            return str(data[0])
        return "请求失败"
