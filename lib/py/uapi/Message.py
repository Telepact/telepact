from typing import Dict, Any


class Message:
    def __init__(self, header: Dict[str, Any], body: Dict[str, Any]):
        self.header = header.copy()
        self.body = body

    def get_body_target(self) -> str:
        entry = next(iter(self.body.items()), None)
        return entry[0] if entry else None

    def get_body_payload(self) -> Dict[str, Any]:
        entry = next(iter(self.body.items()), None)
        return entry[1] if entry else None
