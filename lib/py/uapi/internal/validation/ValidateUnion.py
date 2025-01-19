from typing import TYPE_CHECKING, cast
from uapi.internal.types.UUnion import _UNION_NAME
from uapi.internal.validation.ValidationFailure import ValidationFailure

if TYPE_CHECKING:
    from uapi.internal.validation.ValidateContext import ValidateContext
    from uapi.internal.types.UStruct import UStruct
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration


def validate_union(value: object,
                   name: str, tags: dict[str, 'UStruct'], ctx: 'ValidateContext') -> list['ValidationFailure']:
    from uapi.internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure
    from uapi.internal.validation.ValidateUnionTags import validate_union_tags

    if isinstance(value, dict):
        selected_tags: dict[str, object]
        if name.startswith("fn."):
            selected_tags = {name: ctx.select.get(
                name) if ctx.select else None}
        else:
            selected_tags = cast(
                dict[str, object], ctx.select.get(name) if ctx.select else None)
        return validate_union_tags(tags, selected_tags, value, ctx)
    else:
        return get_type_unexpected_validation_failure([], value, _UNION_NAME)
