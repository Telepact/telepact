import base64
import traceback
from typing import List


class RandomGenerator:
    def __init__(self, collection_length_min: int, collection_length_max: int):
        self.seed = 0
        self.collection_length_min = collection_length_min
        self.collection_length_max = collection_length_max
        self.count = 0
        self.set_seed(0)

    def set_seed(self, seed: int):
        self.seed = (seed & 0x7ffffffe) + 1

    @staticmethod
    def find_stack() -> str:
        stack = traceback.extract_stack()
        for i, frame in enumerate(stack):
            if i == 0:
                continue
            if "_random_generator" not in frame.filename:
                return str(frame)
        raise RuntimeError()

    def next_int(self) -> int:
        x = self.seed
        x ^= x << 13
        x ^= x >> 17
        x ^= x << 5
        self.seed = (x & 0x7ffffffe) + 1
        self.count += 1
        result = self.seed
        # print(f"{self.count} {result} {self.find_stack()}")
        return result

    def next_int_with_ceiling(self, ceiling: int) -> int:
        if ceiling == 0:
            return 0
        return self.next_int() % ceiling

    def next_boolean(self) -> bool:
        return self.next_int_with_ceiling(31) > 15

    def next_string(self) -> str:
        return base64.b64encode(self.next_int().to_bytes(4, 'big')).decode('utf-8')

    def next_double(self) -> float:
        return (self.next_int() & 0x7fffffff) / 0x7fffffff

    def next_collection_length(self) -> int:
        return self.next_int_with_ceiling(self.collection_length_max - self.collection_length_min) + self.collection_length_min
