from typing import Union


class UError:
    def __init__(self, name: str, errors: UUnion):
        self.name = name
        self.errors = errors
