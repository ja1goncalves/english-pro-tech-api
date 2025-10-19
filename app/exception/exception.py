class CredentialsError(Exception):
    def __init__(self, message="Credentials are invalid"):
        self.message = message
        super().__init__(message)

class ForbiddenError(Exception):
    def __init__(self, message="Forbidden"):
        self.message = message
        super().__init__(message)

class UpdateError(Exception):
    def __init__(self, message="No data was updated"):
        self.message = message
        super().__init__(message)

class RoleLevelError(Exception):
    def __init__(self, message="Incorrect role level"):
        self.message = message
        super().__init__(message)