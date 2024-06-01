from typing import List, Dict


class SchemaParseFailure:
    def __init__(self, path: List[object], reason: str, data: Dict[str, object], key: str) -> None:
        self.path = path
        self.reason = reason
        self.data = data
        self.key = key
