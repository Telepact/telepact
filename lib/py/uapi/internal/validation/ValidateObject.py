from typing import Any, Dict, List, Tuple, TYPE_CHECKING

from uapi.internal.types.UObject import _OBJECT_NAME
from uapi.internal.validation.ValidationFailure import ValidationFailure

if TYPE_CHECKING:
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration


def validate_object(value: Any, select: Dict[str, Any], fn: str,
                    type_parameters: List['UTypeDeclaration'],
                    generics: List['UTypeDeclaration']) -> List['ValidationFailure']:
    from uapi.internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure

    if isinstance(value, dict):
        nested_type_declaration = type_parameters[0]

        validation_failures = []
        for k, v in value.items():
            nested_validation_failures = nested_type_declaration.validate(
                v, select, fn, generics)

            nested_validation_failures_with_path = []
            for f in nested_validation_failures:
                this_path = [k] + f.path

                nested_validation_failures_with_path.append(
                    ValidationFailure(this_path, f.reason, f.data))

            validation_failures.extend(nested_validation_failures_with_path)

        return validation_failures
    else:
        return get_type_unexpected_validation_failure([], value, _OBJECT_NAME)
