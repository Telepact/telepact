from typing import List, Dict


class ValidationFailure:
    def __init__(self, path: List[object], reason: str, data: Dict[str, object]):
        self.path = path
        self.reason = reason
        self.data = data
