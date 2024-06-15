from typing import cast


class Message:
    def __init__(self, header: dict[str, object], body: dict[str, object]):
        self.header = header.copy()
        self.body = body

    def get_body_target(self) -> str:
        entry = next(iter(self.body.items()))
        return entry[0]

    def get_body_payload(self) -> dict[str, object]:
        entry = next(iter(self.body.items()))
        return cast(dict[str, object], entry[1])
