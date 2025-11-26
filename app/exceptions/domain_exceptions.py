"""ドメイン層の例外定義"""


class DomainException(Exception):
    """ドメイン層の基底例外"""
    pass


class ResourceNotFoundException(DomainException):
    """リソースが見つからない"""
    def __init__(self, resource_type: str, resource_id: str):
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(f"{resource_type} not found: {resource_id}")


class UnauthorizedAccessException(DomainException):
    """権限がない"""
    def __init__(self, message: str = "アクセス権限がありません"):
        super().__init__(message)


class ValidationException(DomainException):
    """バリデーションエラー"""
    def __init__(self, message: str):
        super().__init__(message)


class DuplicateResourceException(DomainException):
    """リソースの重複"""
    def __init__(self, resource_type: str, identifier: str):
        self.resource_type = resource_type
        self.identifier = identifier
        super().__init__(f"{resource_type} already exists: {identifier}")

