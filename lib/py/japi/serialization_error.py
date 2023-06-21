class SerializationError(RuntimeError):
    def __init__(self, cause: Exception) -> None:
        super().__init__(str(cause))
