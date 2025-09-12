from rest_framework.response import Response


def StandardResponse(code=200, message="成功", data=None, status=200):
    return Response({
        "code": code,
        "message": message,
        "data": data
    }, status=status)

