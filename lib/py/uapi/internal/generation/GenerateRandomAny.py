from typing import Any
from uapi import RandomGenerator


def generate_random_any(random_generator: 'RandomGenerator') -> Any:
    select_type = random_generator.next_int_with_ceiling(3)
    if select_type == 0:
        return random_generator.next_boolean()
    elif select_type == 1:
        return random_generator.next_int()
    else:
        return random_generator.next_string()
