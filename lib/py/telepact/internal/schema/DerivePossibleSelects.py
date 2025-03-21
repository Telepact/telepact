from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..types.VUnion import VUnion
    from ..types.VStruct import VStruct
    from ..types.VType import VType
    from ..types.VFieldDeclaration import VFieldDeclaration


def derive_possible_select(fn_name: str, result: 'VUnion') -> dict[str, object]:
    from ..types.VUnion import VUnion
    from ..types.VStruct import VStruct

    nested_types: dict[str, VType] = {}
    ok_fields: dict[str, VFieldDeclaration] = result.tags['Ok_'].fields

    ok_field_names = sorted(ok_fields.keys())

    find_nested_types(ok_fields, nested_types)

    possible_select: dict[str, object] = {}

    possible_select['->'] = {
        'Ok_': ok_field_names,
    }

    sorted_type_keys = sorted(nested_types.keys())
    for k in sorted_type_keys:
        v = nested_types[k]
        if isinstance(v, VUnion):
            union_select: dict[str, list[str]] = {}
            sorted_tag_keys = sorted(v.tags.keys())
            for c in sorted_tag_keys:
                typ = v.tags[c]
                selected_field_names: list[str] = sorted(typ.fields.keys())
                union_select[c] = selected_field_names

            possible_select[k] = union_select
        elif isinstance(v, VStruct):
            struct_select: list[str] = sorted(v.fields.keys())
            possible_select[k] = struct_select

    return possible_select


def find_nested_types(fields: dict[str, 'VFieldDeclaration'], nested_types: dict[str, 'VType']) -> None:
    from ..types.VUnion import VUnion
    from ..types.VStruct import VStruct

    for field in fields.values():
        typ = field.type_declaration.type
        if isinstance(typ, VUnion):
            nested_types[typ.name] = typ
            for c in typ.tags.values():
                find_nested_types(c.fields, nested_types)
        elif isinstance(typ, VStruct):
            nested_types[typ.name] = typ
            find_nested_types(typ.fields, nested_types)
