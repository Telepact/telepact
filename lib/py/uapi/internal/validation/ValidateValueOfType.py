from typing import Any, Dict, List, Optional
from uapi.internal.validation.GetTypeUnexpectedValidationFailure import getTypeUnexpectedValidationFailure
from uapi.internal.types.UGeneric import UGeneric
from uapi.internal.types.UType import UType
from uapi.internal.types.UTypeDeclaration import UTypeDeclaration


def validate_value_of_type(value: Any, select: Dict[str, Any], fn: str,
                           generics: List[UTypeDeclaration], this_type: UType,
                           nullable: bool, type_parameters: List[UTypeDeclaration]) -> List[ValidationFailure]:
    if value is None:
        is_nullable = nullable
        if isinstance(this_type, UGeneric):
            generic_index = this_type.index
            generic = generics[generic_index]
            is_nullable = generic.nullable

        if not is_nullable:
            return getTypeUnexpectedValidationFailure([], value, this_type.get_name(generics))
        else:
            return []

    return this_type.validate(value, select, fn, type_parameters, generics)
