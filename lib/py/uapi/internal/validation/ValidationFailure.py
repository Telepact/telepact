from typing import list, dict


class ValidationFailure:
    def __init__(self, path: list[object], reason: str, data: dict[str, object]):
        self.path = path
        self.reason = reason
        self.data = data
