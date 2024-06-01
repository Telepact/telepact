from typing import List, Dict
from uapi.internal.types import UStruct, UTypeDeclaration
from uapi.internal.validation.ValidateStructFields import validate_struct_fields


def validate_union_struct(
    union_struct: UStruct,
    union_case: str,
    actual: Dict[str, object],
    selected_cases: Dict[str, object],
    select: Dict[str, object],
    fn: str,
    type_parameters: List[UTypeDeclaration]
) -> List[ValidationFailure]:
    selected_fields = selected_cases.get(
        union_case) if selected_cases else None
    return validate_struct_fields(
        union_struct.fields,
        selected_fields,
        actual,
        select,
        fn,
        type_parameters
    )
