from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .VUnion import VUnion


class VError:
    def __init__(self, name: str, errors: 'VUnion'):
        self.name = name
        self.errors = errors
