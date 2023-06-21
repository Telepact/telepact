class JapiParseError(RuntimeError):
    def __init__(self, message: str, cause: Exception = None):
        super().__init__(message, cause)
