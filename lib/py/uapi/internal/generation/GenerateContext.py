from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.RandomGenerator import RandomGenerator


class GenerateContext:
    include_optional_fields: bool
    randomize_optional_fields: bool
    always_include_required_fields: bool
    fn_scope: str
    random_generator: 'RandomGenerator'

    def __init__(self, include_optional_fields: bool,
                 randomize_optional_fields: bool, always_include_required_fields: bool,
                 fn_scope: str, random_generator: 'RandomGenerator') -> None:
        self.include_optional_fields = include_optional_fields
        self.randomize_optional_fields = randomize_optional_fields
        self.always_include_required_fields = always_include_required_fields
        self.fn_scope = fn_scope
        self.random_generator = random_generator

    def copy(self, include_optional_fields: bool | None = None,
             randomize_optional_fields: bool | None = None, always_include_required_fields: bool | None = None,
             fn_scope: str | None = None, random_generator: 'RandomGenerator | None' = None) -> 'GenerateContext':
        return GenerateContext(include_optional_fields if include_optional_fields is not None else self.include_optional_fields,
                               randomize_optional_fields if randomize_optional_fields is not None else self.randomize_optional_fields,
                               always_include_required_fields if always_include_required_fields is not None else self.always_include_required_fields,
                               fn_scope if fn_scope is not None else self.fn_scope,
                               random_generator if random_generator is not None else self.random_generator)
