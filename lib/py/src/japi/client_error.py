from typing import Dict


class ClientError(RuntimeError):
    def __init__(self, type_: str, body: Dict[str, object]):
        error_message = f"{type_}: {body}"
        super().__init__(error_message)
        self.type = type_
        self.body = body
