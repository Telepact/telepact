from typing import TYPE_CHECKING


from uapi.internal.binary.BinaryEncoding import BinaryEncoding

if TYPE_CHECKING:
    from uapi.UApiSchema import UApiSchema


def construct_binary_encoding(u_api_schema: 'UApiSchema') -> BinaryEncoding:
    from uapi.internal.binary.CreateChecksum import create_checksum
    from uapi.internal.types.UUnion import UUnion
    from uapi.internal.types.UStruct import UStruct
    from uapi.internal.types.UFn import UFn
    from uapi.internal.types.UFieldDeclaration import UFieldDeclaration

    all_keys: set[str] = set()

    for key, value in u_api_schema.parsed.items():
        all_keys.add(key)

        if isinstance(value, UStruct):
            struct_fields: dict[str, UFieldDeclaration] = value.fields
            all_keys.update(struct_fields.keys())
        elif isinstance(value, UUnion):
            union_tags: dict[str, UStruct] = value.tags
            for tag_key, tag_value in union_tags.items():
                all_keys.add(tag_key)
                struct_fields = tag_value.fields
                all_keys.update(struct_fields.keys())
        elif isinstance(value, UFn):
            fn_call_tags: dict[str, UStruct] = value.call.tags
            fn_result_tags: dict[str, UStruct] = value.result.tags

            for tag_key, tag_value in fn_call_tags.items():
                all_keys.add(tag_key)
                struct_fields = tag_value.fields
                all_keys.update(struct_fields.keys())

            for tag_key, tag_value in fn_result_tags.items():
                all_keys.add(tag_key)
                struct_fields = tag_value.fields
                all_keys.update(struct_fields.keys())

    sorted_all_keys = sorted(all_keys)
    binary_encoding = {key: i for i, key in enumerate(sorted_all_keys)}
    final_string = "\n".join(sorted_all_keys)
    checksum = create_checksum(final_string)
    return BinaryEncoding(binary_encoding, checksum)
