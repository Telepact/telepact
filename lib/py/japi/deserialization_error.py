class DeserializationError(RuntimeError):
    def __init__(self, cause):
        super().__init__(str(cause))
