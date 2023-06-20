class ApplicationError(RuntimeError):
    def __init__(self, message_type: str, body: dict):
        self.message_type = message_type
        self.body = body
