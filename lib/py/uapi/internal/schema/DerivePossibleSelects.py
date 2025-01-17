from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uapi.internal.types.UUnion import UUnion
    from uapi.internal.types.UStruct import UStruct
    from uapi.internal.types.UType import UType
    from uapi.internal.types.UFieldDeclaration import UFieldDeclaration


def derive_possible_select(fn_name: str, result: 'UUnion') -> dict[str, object]:
    from uapi.internal.types.UUnion import UUnion
    from uapi.internal.types.UStruct import UStruct

    nested_types: dict[str, UType] = {}
    ok_fields: dict[str, UFieldDeclaration] = result.cases['Ok_'].fields

    ok_field_names = sorted(ok_fields.keys())

    find_nested_types(ok_fields, nested_types)

    possible_select: dict[str, object] = {}

    possible_select['->'] = {
        'Ok_': ok_field_names,
    }

    sorted_type_keys = sorted(nested_types.keys())
    for k in sorted_type_keys:
        print(f'k: {k}')
        v = nested_types[k]
        if isinstance(v, UUnion):
            union_select: dict[str, list[str]] = {}
            sorted_case_keys = sorted(v.cases.keys())
            for c in sorted_case_keys:
                typ = v.cases[c]
                selected_field_names: list[str] = sorted(typ.fields.keys())
                union_select[c] = selected_field_names

            possible_select[k] = union_select
        elif isinstance(v, UStruct):
            struct_select: list[str] = sorted(v.fields.keys())
            possible_select[k] = struct_select

    return possible_select


def find_nested_types(fields: dict[str, 'UFieldDeclaration'], nested_types: dict[str, 'UType']) -> None:
    from uapi.internal.types.UUnion import UUnion
    from uapi.internal.types.UStruct import UStruct

    for field in fields.values():
        typ = field.type_declaration.type
        if isinstance(typ, UUnion):
            nested_types[typ.name] = typ
            for c in typ.cases.values():
                find_nested_types(c.fields, nested_types)
        elif isinstance(typ, UStruct):
            nested_types[typ.name] = typ
            find_nested_types(typ.fields, nested_types)
