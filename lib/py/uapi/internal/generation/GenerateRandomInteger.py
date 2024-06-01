from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from uapi.RandomGenerator import RandomGenerator


def generate_random_integer(blueprint_value: Any, use_blueprint_value: bool,
                            random_generator: 'RandomGenerator') -> Any:
    if use_blueprint_value:
        return blueprint_value
    else:
        return random_generator.next_int()
