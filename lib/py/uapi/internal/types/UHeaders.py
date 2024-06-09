from typing import dict, TYPE_CHECKING

if TYPE_CHECKING:
    from uapi.internal.types.UFieldDeclaration import UFieldDeclaration


class UHeaders:
    def __init__(
            self,
            name: str,
            requestHeaders: dict[str, 'UFieldDeclaration'],
            responseHeaders: dict[str, 'UFieldDeclaration']
    ) -> None:
        self.name = name
        self.requestHeaders = requestHeaders
        self.responseHeaders = responseHeaders
