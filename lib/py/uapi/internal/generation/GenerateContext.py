from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.RandomGenerator import RandomGenerator


class GenerateContext:
    blueprint_value: object
    use_blueprint_value: bool
    include_optional_fields: bool
    randomize_optional_fields: bool
    always_include_required_fields: bool
    type_parameters: list['UTypeDeclaration']
    random_generator: 'RandomGenerator'

    def __init__(self, blueprint_value: object, use_blueprint_value: bool, include_optional_fields: bool,
                 randomize_optional_fields: bool, always_include_required_fields: bool, type_parameters: list['UTypeDeclaration'],
                 random_generator: 'RandomGenerator') -> None:
        self.blueprint_value = blueprint_value
        self.use_blueprint_value = use_blueprint_value
        self.include_optional_fields = include_optional_fields
        self.randomize_optional_fields = randomize_optional_fields
        self.always_include_required_fields = always_include_required_fields
        self.type_parameters = type_parameters
        self.random_generator = random_generator

    def copy(self, blueprint_value: object | None = None, use_blueprint_value: bool | None = None, include_optional_fields: bool | None = None,
             randomize_optional_fields: bool | None = None, always_include_required_fields: bool | None = None, type_parameters: list['UTypeDeclaration'] | None = None,
             random_generator: 'RandomGenerator | None' = None) -> 'GenerateContext':
        return GenerateContext(blueprint_value if blueprint_value is not None else self.blueprint_value,
                               use_blueprint_value if use_blueprint_value is not None else self.use_blueprint_value,
                               include_optional_fields if include_optional_fields is not None else self.include_optional_fields,
                               randomize_optional_fields if randomize_optional_fields is not None else self.randomize_optional_fields,
                               always_include_required_fields if always_include_required_fields is not None else self.always_include_required_fields,
                               type_parameters if type_parameters is not None else self.type_parameters,
                               random_generator if random_generator is not None else self.random_generator)
