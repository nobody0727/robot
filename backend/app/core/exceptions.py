class AppException(Exception):
    def __init__(self, status_code: int, message: str, code: int = None):
        self.status_code = status_code
        self.message = message
        self.code = code
        super().__init__(self.message)


class AuthenticationError(AppException):
    def __init__(self, message: str = "认证失败"):
        super().__init__(status_code=401, message=message, code=1001)


class TokenExpiredError(AuthenticationError):
    def __init__(self, message: str = "Token已过期"):
        super().__init__(message=message)
        self.code = 1002


class TokenInvalidError(AuthenticationError):
    def __init__(self, message: str = "无效的Token"):
        super().__init__(message=message)
        self.code = 1003


class PermissionDeniedError(AppException):
    def __init__(self, message: str = "权限不足"):
        super().__init__(status_code=403, message=message, code=1004)


class UserNotFoundError(AppException):
    def __init__(self, message: str = "用户不存在"):
        super().__init__(status_code=404, message=message, code=1005)


class InvalidCredentialsError(AuthenticationError):
    def __init__(self, message: str = "用户名或密码错误"):
        super().__init__(message=message)
        self.code = 1001


class UserAlreadyExistsError(AppException):
    def __init__(self, message: str = "用户已存在"):
        super().__init__(status_code=400, message=message, code=1006)


class WhitelistUserNotFoundError(AppException):
    def __init__(self, message: str = "白名单用户不存在"):
        super().__init__(status_code=404, message=message, code=2001)


class WhitelistUserExistsError(AppException):
    def __init__(self, message: str = "白名单用户已存在"):
        super().__init__(status_code=400, message=message, code=2002)


class WhitelistImportError(AppException):
    def __init__(self, message: str = "导入失败"):
        super().__init__(status_code=400, message=message, code=2003)


class GroupNotFoundError(AppException):
    def __init__(self, message: str = "群组不存在"):
        super().__init__(status_code=404, message=message, code=3001)


class GroupAlreadyExistsError(AppException):
    def __init__(self, message: str = "群组已存在"):
        super().__init__(status_code=400, message=message, code=3002)


class MessageNotFoundError(AppException):
    def __init__(self, message: str = "消息不存在"):
        super().__init__(status_code=404, message=message, code=3003)


class AIServiceUnavailableError(AppException):
    def __init__(self, message: str = "AI服务暂不可用"):
        super().__init__(status_code=503, message=message, code=4001)


class AIRateLimitError(AppException):
    def __init__(self, message: str = "AI服务调用频率超限"):
        super().__init__(status_code=429, message=message, code=4002)


class AIInvalidResponseError(AppException):
    def __init__(self, message: str = "AI服务响应无效"):
        super().__init__(status_code=502, message=message, code=4003)


class ConfigNotFoundError(AppException):
    def __init__(self, message: str = "配置项不存在"):
        super().__init__(status_code=404, message=message, code=5001)
