from uapi import RandomGenerator


def generate_random_string(blueprint_value: object, use_blueprint_value: bool,
                           random_generator: RandomGenerator) -> object:
    if use_blueprint_value:
        return blueprint_value
    else:
        return random_generator.next_string()
