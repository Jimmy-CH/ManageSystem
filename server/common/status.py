

class CustomStatus:
    """
    自定义业务状态码，同时提供对应的 HTTP 状态码
    """

    # 成功 (HTTP 2xx)
    SUCCESS = 200          # 业务成功，HTTP 200
    CREATED_SUCCESS = 201   # 直接使用 HTTP 201
    UPDATED_SUCCESS = 200   # 更新成功通常也用 200

    # 客户端错误 (HTTP 4xx)
    VALIDATION_ERROR = 400  # 数据验证失败 → HTTP 400
    AUTH_FAILED = 401       # 认证失败 → HTTP 401
    PERMISSION_DENIED = 403 # 权限不足 → HTTP 403
    NOT_FOUND = 404         # 资源未找到 → HTTP 404

    # 服务器错误 (HTTP 5xx)
    SERVER_ERROR = 500      # 服务器内部错误 → HTTP 500
    DATABASE_ERROR = 500    # 数据库错误也归为 500

    # 业务码 -> (消息, HTTP状态码)
    _code_meta = {
        SUCCESS: ("成功", 200),
        CREATED_SUCCESS: ("创建成功", 201),
        UPDATED_SUCCESS: ("更新成功", 200),
        VALIDATION_ERROR: ("数据验证失败", 400),
        AUTH_FAILED: ("认证失败", 401),
        PERMISSION_DENIED: ("权限不足", 403),
        NOT_FOUND: ("资源未找到", 404),
        SERVER_ERROR: ("服务器内部错误", 500),
        DATABASE_ERROR: ("数据库操作失败", 500),
    }

    @classmethod
    def get_msg(cls, code):
        return cls._code_meta.get(code, ("未知错误", 500))[0]

    @classmethod
    def get_http_status(cls, code):
        return cls._code_meta.get(code, ("未知错误", 500))[1]

