class ClientProcessError(RuntimeError):
    def __init__(self, cause: Exception):
        super().__init__(str(cause))
