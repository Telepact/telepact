from typing import Any, Dict, List, Tuple
from uapi.internal.types import UObject
from uapi.internal.validation import GetTypeUnexpectedValidationFailure
from uapi.internal.types import UTypeDeclaration


def validate_object(value: Any, select: Dict[str, Any], fn: str,
                    type_parameters: List[UTypeDeclaration],
                    generics: List[UTypeDeclaration]) -> List[ValidationFailure]:
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
        return getTypeUnexpectedValidationFailure([], value, UObject._OBJECT_NAME)
