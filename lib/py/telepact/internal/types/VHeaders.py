from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .VFieldDeclaration import VFieldDeclaration


class VHeaders:
    def __init__(
            self,
            name: str,
            request_headers: dict[str, 'VFieldDeclaration'],
            response_headers: dict[str, 'VFieldDeclaration']
    ) -> None:
        self.name = name
        self.request_headers = request_headers
        self.response_headers = response_headers
