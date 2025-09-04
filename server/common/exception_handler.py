
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response:
        response.data = {
            'message': '请求失败',
            'errors': response.data
        }
    return response
