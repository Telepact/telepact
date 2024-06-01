from typing import Dict

from uapi.internal.types.UFieldDeclaration import UFieldDeclaration


class UHeaders:
    def __init__(
            self,
            name: str,
            requestHeaders: Dict[str, UFieldDeclaration],
            responseHeaders: Dict[str, UFieldDeclaration]
    ) -> None:
        self.name = name
        self.requestHeaders = requestHeaders
        self.responseHeaders = responseHeaders
