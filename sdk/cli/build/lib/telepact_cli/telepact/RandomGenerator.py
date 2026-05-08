#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

import inspect
import math
from ctypes import c_int32


def _find_stack() -> str:
    stack = inspect.stack()
    for i in range(1, len(stack)):
        stack_str = f'{stack[i]}'
        if 'RandomGenerator' not in stack_str:
            return f'{stack[i].function} {stack[i-1].function}'
    return 'unknown'

words = [
    "alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta",
    "iota", "kappa", "lambda", "mu", "nu", "xi", "omicron", "pi",
    "rho", "sigma", "tau", "upsilon", "phi", "chi", "psi", "omega"
]

class RandomGenerator:
    def __init__(self, collection_length_min: int, collection_length_max: int):
        self.set_seed(0)
        self.collection_length_min = collection_length_min
        self.collection_length_max = collection_length_max
        self.count = 0

    def set_seed(self, seed: int) -> None:
        self.seed = c_int32(1) if seed == 0 else c_int32(seed)

    def next_int(self) -> int:
        x: c_int32 = c_int32(self.seed.value)
        x = c_int32(x.value ^ (x.value << 16))
        x = c_int32(x.value ^ (x.value >> 11))
        x = c_int32(x.value ^ (x.value << 5))
        self.seed = c_int32(1) if x.value == 0 else c_int32(x.value)
        self.count += 1
        result = c_int32(self.seed.value & 0x7fffffff)
        # print(f'{self.count} {result} {_find_stack()}')
        return result.value

    def next_int_with_ceiling(self, ceiling: int) -> int:
        if ceiling == 0:
            return 0
        return self.next_int() % ceiling

    def next_boolean(self) -> bool:
        return self.next_int_with_ceiling(31) > 15
    
    def next_bytes(self) -> bytes:
        import struct
        return struct.pack(">i", self.next_int())

    def next_string(self) -> str:
        index = self.next_int_with_ceiling(len(words))
        return words[index]

    def next_double(self) -> float:
        return float(self.next_int() & 0x7fffffff) / float(0x7fffffff)

    def next_collection_length(self) -> int:
        return self.next_int_with_ceiling(self.collection_length_max - self.collection_length_min) + self.collection_length_min
