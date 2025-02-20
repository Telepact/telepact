from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...internal.types.UFieldDeclaration import UFieldDeclaration


class UHeaders:
    def __init__(
            self,
            name: str,
            request_headers: dict[str, 'UFieldDeclaration'],
            response_headers: dict[str, 'UFieldDeclaration']
    ) -> None:
        self.name = name
        self.request_headers = request_headers
        self.response_headers = response_headers
