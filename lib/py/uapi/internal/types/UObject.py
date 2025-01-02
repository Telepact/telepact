from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.validation.ValidationFailure import ValidationFailure

from uapi.internal.types.UType import UType

_OBJECT_NAME: str = "Object"


class UObject(UType):

    def get_type_parameter_count(self) -> int:
        return 1

    def validate(self, value: object, select: dict[str, object] | None, fn: str | None,
                 type_parameters: list['UTypeDeclaration']) -> list['ValidationFailure']:
        from uapi.internal.validation.ValidateObject import validate_object
        return validate_object(value, select, fn, type_parameters)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool,
                              include_optional_fields: bool, randomize_optional_fields: bool,
                              type_parameters: list['UTypeDeclaration'],
                              random_generator: 'RandomGenerator') -> object:
        from uapi.internal.generation.GenerateRandomObject import generate_random_object
        return generate_random_object(blueprint_value, use_blueprint_value, include_optional_fields,
                                      randomize_optional_fields, type_parameters, random_generator)

    def get_name(self) -> str:
        return _OBJECT_NAME
