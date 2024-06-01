class UApiError(Exception):
    """
    Indicates critical failure in uAPI processing logic.
    """

    def __init__(self, message: str = '', cause: Exception = None):
        super().__init__(message)
        self.cause = cause
