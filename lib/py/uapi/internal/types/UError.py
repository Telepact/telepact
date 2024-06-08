from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uapi.internal.types.UUnion import UUnion


class UError:
    def __init__(self, name: str, errors: 'UUnion'):
        self.name = name
        self.errors = errors
