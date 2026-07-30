#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .TFieldDeclaration import TFieldDeclaration


class THeaders:
    def __init__(
            self,
            name: str,
            request_headers: dict[str, 'TFieldDeclaration'],
            response_headers: dict[str, 'TFieldDeclaration']
    ) -> None:
        self.name = name
        self.request_headers = request_headers
        self.response_headers = response_headers
