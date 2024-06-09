class BinaryPackNode:
    def __init__(self, value: int | None, nested: dict[int, 'BinaryPackNode']):
        self.value = value
        self.nested = nested
