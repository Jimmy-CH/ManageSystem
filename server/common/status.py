

class CustomStatus:
    """
    自定义业务状态码与消息映射
    """

    # 成功
    SUCCESS = 0
    CREATED_SUCCESS = 2001
    UPDATED_SUCCESS = 2002

    # 客户端错误
    VALIDATION_ERROR = 4001
    AUTH_FAILED = 4002
    PERMISSION_DENIED = 4003
    NOT_FOUND = 4004

    # 服务器错误
    SERVER_ERROR = 5001
    DATABASE_ERROR = 5002

    # 状态码 -> 消息 映射
    _code_to_msg = {
        SUCCESS: "成功",
        CREATED_SUCCESS: "创建成功",
        UPDATED_SUCCESS: "更新成功",
        VALIDATION_ERROR: "数据验证失败",
        AUTH_FAILED: "认证失败",
        PERMISSION_DENIED: "权限不足",
        NOT_FOUND: "资源未找到",
        SERVER_ERROR: "服务器内部错误",
        DATABASE_ERROR: "数据库操作失败",
    }

    @classmethod
    def get_msg(cls, code):
        return cls._code_to_msg.get(code, "未知错误")
