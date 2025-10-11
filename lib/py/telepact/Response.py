from typing import NamedTuple

class Response(NamedTuple):
    bytes: bytes
    headers: dict[str, object]

