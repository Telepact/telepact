from typing import List, Dict, TYPE_CHECKING
from uapi.internal.validation.ValidationFailure import ValidationFailure

if TYPE_CHECKING:
    from uapi.internal.types.UStruct import UStruct
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration


def validate_union_struct(
    union_struct: 'UStruct',
    union_case: str,
    actual: Dict[str, object],
    selected_cases: Dict[str, object],
    select: Dict[str, object],
    fn: str,
    type_parameters: List['UTypeDeclaration']
) -> List['ValidationFailure']:
    selected_fields = selected_cases.get(
        union_case) if selected_cases else None
    from uapi.internal.validation.ValidateStructFields import validate_struct_fields

    return validate_struct_fields(
        union_struct.fields,
        selected_fields,
        actual,
        select,
        fn,
        type_parameters
    )
