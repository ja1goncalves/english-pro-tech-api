class CredentialsError(Exception):
    def __init__(self, message="Credentials are invalid"):
        super().__init__(message)

class ForbiddenError(Exception):
    def __init__(self, message="Forbidden"):
        super().__init__(message)

class UpdateError(Exception):
    def __init__(self, message="No data was updated"):
        super().__init__(message)