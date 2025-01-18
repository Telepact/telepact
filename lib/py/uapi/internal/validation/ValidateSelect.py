from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from uapi.internal.validation.ValidateContext import ValidateContext
    from uapi.internal.validation.ValidationFailure import ValidationFailure


def validate_select(given_obj: object, possible_fn_selects: dict[str, object], ctx: 'ValidateContext') -> list['ValidationFailure']:
    from uapi.internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure

    if not isinstance(given_obj, dict):
        return get_type_unexpected_validation_failure([], given_obj, 'Object')

    fn_scope = cast(str, ctx.fn)

    possible_select = possible_fn_selects[fn_scope]

    return is_sub_select([], given_obj, possible_select)


def is_sub_select(path: list[object], given_obj: object, possible_select_section: object) -> list['ValidationFailure']:
    from uapi.internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure
    from uapi.internal.validation.ValidationFailure import ValidationFailure

    if isinstance(possible_select_section, list):
        if not isinstance(given_obj, list):
            return get_type_unexpected_validation_failure(path, given_obj, 'Array')

        validation_failures = []

        for index, element in enumerate(given_obj):
            if element not in possible_select_section:
                validation_failures.append(ValidationFailure(
                    path + [index], 'ArrayElementDisallowed', {}))

        return validation_failures

    elif isinstance(possible_select_section, dict):
        if not isinstance(given_obj, dict):
            return get_type_unexpected_validation_failure(path, given_obj, 'Object')

        validation_failures = []

        for key, value in given_obj.items():
            if key in possible_select_section:
                inner_failures = is_sub_select(
                    path + [key], value, possible_select_section[key])
                validation_failures.extend(inner_failures)
            else:
                validation_failures.append(ValidationFailure(
                    path + [key], 'ObjectKeyDisallowed', {}))

        return validation_failures

    return []
