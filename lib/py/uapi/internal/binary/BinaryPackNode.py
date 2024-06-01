from typing import Dict, Optional


class BinaryPackNode:
    def __init__(self, value: Optional[int], nested: Dict[int, 'BinaryPackNode']):
        self.value = value
        self.nested = nested
