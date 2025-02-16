from typing import List, Dict, Tuple, Set, Union
from typing import TYPE_CHECKING


from uapi.internal.binary.BinaryEncoding import BinaryEncoding
from uapi.internal.binary.CreateChecksum import create_checksum

if TYPE_CHECKING:
    from uapi.UApiSchema import UApiSchema
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration


def trace_type(type_declaration: 'UTypeDeclaration') -> list[str]:
    from uapi.internal.types.UArray import UArray
    from uapi.internal.types.UObject import UObject
    from uapi.internal.types.UStruct import UStruct
    from uapi.internal.types.UUnion import UUnion

    this_all_keys: list[str] = []

    if isinstance(type_declaration.type, UArray):
        these_keys2 = trace_type(type_declaration.type_parameters[0])
        this_all_keys.extend(these_keys2)
    elif isinstance(type_declaration.type, UObject):
        these_keys2 = trace_type(type_declaration.type_parameters[0])
        this_all_keys.extend(these_keys2)
    elif isinstance(type_declaration.type, UStruct):
        struct_fields = type_declaration.type.fields
        for struct_field_key, struct_field in struct_fields.items():
            this_all_keys.append(struct_field_key)
            more_keys = trace_type(struct_field.type_declaration)
            this_all_keys.extend(more_keys)
    elif isinstance(type_declaration.type, UUnion):
        union_tags = type_declaration.type.tags
        for tag_key, tag_value in union_tags.items():
            this_all_keys.append(tag_key)
            struct_fields = tag_value.fields
            for struct_field_key, struct_field in struct_fields.items():
                this_all_keys.append(struct_field_key)
                more_keys = trace_type(struct_field.type_declaration)
                this_all_keys.extend(more_keys)

    return this_all_keys


def construct_binary_encoding(u_api_schema: 'UApiSchema') -> 'BinaryEncoding':
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.types.UFn import UFn

    all_keys: set[str] = set()

    functions: list[Tuple[str, UFn]] = []

    for key, value in u_api_schema.parsed.items():
        if isinstance(value, UFn):
            functions.append((key, value))

    for key, value in functions:
        all_keys.add(key)
        args = value.call.tags[key]
        for field_key, field in args.fields.items():
            all_keys.add(field_key)
            keys = trace_type(field.type_declaration)
            for key in keys:
                all_keys.add(key)

        result = value.result.tags['Ok_']
        all_keys.add('Ok_')
        for field_key, field in result.fields.items():
            all_keys.add(field_key)
            keys = trace_type(field.type_declaration)
            for key in keys:
                all_keys.add(key)

    sorted_all_keys = sorted(all_keys)

    print('Sorted all keys:')
    binary_encoding = {key: i for i, key in enumerate(sorted_all_keys)}
    final_string = "\n".join(sorted_all_keys)
    checksum = create_checksum(final_string)
    return BinaryEncoding(binary_encoding, checksum)
