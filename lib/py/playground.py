import uapi.types
import uapi._util
from ..._util_types import _RandomGenerator

if __name__ == '__main__':
    r = _RandomGenerator(3, 3)

    for i in range(0, 100):
        r.next_int()
        print(r.seed.value)
