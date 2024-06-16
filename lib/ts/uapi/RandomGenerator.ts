import inspect
import math
from ctypes import c_int32


def _find_stack() -> str:
    i = 0
    for stack in inspect.stack():
        i += 1
        if i == 1:
            continue
        stack_str = f'{stack}'
        if not '_util_types.py' in stack_str:
            return f'{stack.function}'
    return 'unknown'


class RandomGenerator:
    def __init__(self, collection_length_min: int, collection_length_max: int):
        self.set_seed(0)
        self.collection_length_min = collection_length_min
        self.collection_length_max = collection_length_max
        self.count = 0

    def set_seed(self, seed: int) -> None:
        self.seed = c_int32((seed & 0x7ffffffe) + 1)

    def next_int(self) -> int:
        x: c_int32 = c_int32(self.seed.value)
        x = c_int32(x.value ^ (x.value << 13))
        x = c_int32(x.value ^ (x.value >> 17))
        x = c_int32(x.value ^ (x.value << 5))
        self.seed = c_int32((x.value & 0x7ffffffe) + 1)
        self.count += 1
        result = self.seed.value
        # print(f'{self.count} {result} {_find_stack()}')
        return result

    def next_int_with_ceiling(self, ceiling: int) -> int:
        if ceiling == 0:
            return 0
        return self.next_int() % ceiling

    def next_boolean(self) -> bool:
        return self.next_int_with_ceiling(31) > 15

    def next_string(self) -> str:
        import base64
        import struct
        bytes_data = struct.pack(">i", self.next_int())
        return base64.b64encode(bytes_data).decode().rstrip("=")

    def next_double(self) -> float:
        return float(self.next_int() & 0x7fffffff) / float(0x7fffffff)

    def next_collection_length(self) -> int:
        return self.next_int_with_ceiling(self.collection_length_max - self.collection_length_min) + self.collection_length_min
