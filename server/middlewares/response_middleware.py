# middleware.py
import json
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.core.serializers.json import DjangoJSONEncoder


class UnifiedResponseMiddleware(MiddlewareMixin):
    """
    统一响应格式中间件
    格式: {"code": 0, "message": "success", "data": {...}}
    """

    def process_response(self, request, response):
        # 只处理 API 请求（可以根据需要调整判断条件）
        if not self._is_api_request(request):
            return response

        # 已经是标准响应格式的直接返回
        if self._is_standard_response(response):
            return response

        # 处理不同类型的响应
        if isinstance(response, JsonResponse):
            return self._handle_json_response(response)
        elif hasattr(response, 'data'):
            return self._create_success_response(response.data)
        else:
            # 普通 HttpResponse
            return self._create_success_response({'content': response.content.decode()})

    def _is_api_request(self, request):
        """判断是否为 API 请求"""
        api_paths = ['/api/', '/rest/']
        return any(path in request.path for path in api_paths)

    def _is_standard_response(self, response):
        """判断是否已经是标准响应格式"""
        if hasattr(response, 'data') and isinstance(response.data, dict):
            return 'code' in response.data and 'message' in response.data
        return False

    def _handle_json_response(self, response):
        """处理 JsonResponse"""
        try:
            content = json.loads(response.content)
            if isinstance(content, dict) and 'code' in content:
                return response
            return self._create_success_response(content)
        except:
            return self._create_success_response({'content': response.content.decode()})

    def _create_success_response(self, data=None):
        """创建成功响应"""
        response_data = {
            'code': 0,
            'message': 'success',
            'data': data or {}
        }
        return JsonResponse(response_data, encoder=DjangoJSONEncoder, json_dumps_params={'ensure_ascii': False})

    def _create_error_response(self, message, code=-1, data=None):
        """创建错误响应"""
        response_data = {
            'code': code,
            'message': message,
            'data': data or {}
        }
        return JsonResponse(response_data, status=400, encoder=DjangoJSONEncoder,
                            json_dumps_params={'ensure_ascii': False})

