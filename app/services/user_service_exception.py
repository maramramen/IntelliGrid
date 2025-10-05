class PasswordUpdateRequiredException(Exception):
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code
class InvalidUsernameOrPasswordException(Exception):
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code