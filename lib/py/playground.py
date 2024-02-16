import uapi.types
import uapi._util
from uapi._util_types import _RandomGenerator

r = _RandomGenerator(3, 3)

for i in range(0, 100):
    r.next_int()
    print(r.seed.value)
