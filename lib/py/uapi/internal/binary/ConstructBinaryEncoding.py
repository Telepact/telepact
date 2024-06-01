from typing import Dict, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from uapi import UApiSchema
    from uapi.internal.binary.BinaryEncoding import BinaryEncoding


def construct_binary_encoding(u_api_schema: 'UApiSchema') -> 'BinaryEncoding':
    from uapi.internal.binary.CreateChecksum import create_checksum
    from uapi.internal.types.UUnion import UUnion
    from uapi.internal.types.UStruct import UStruct
    from uapi.internal.types.UFn import UFn

    all_keys = set()
    for key, value in u_api_schema.parsed.items():
        all_keys.add(key)

        if isinstance(value, UStruct):
            struct_fields = value.fields
            all_keys.update(struct_fields.keys())
        elif isinstance(value, UUnion):
            union_cases = value.cases
            for case_key, struct in union_cases.items():
                all_keys.add(case_key)
                struct_fields = struct.fields
                all_keys.update(struct_fields.keys())
        elif isinstance(value, UFn):
            fn_call = value.call
            fn_call_cases = fn_call.cases
            fn_result = value.result
            fn_result_cases = fn_result.cases

            for case_key, struct in fn_call_cases.items():
                all_keys.add(case_key)
                struct_fields = struct.fields
                all_keys.update(struct_fields.keys())

            for case_key, struct in fn_result_cases.items():
                all_keys.add(case_key)
                struct_fields = struct.fields
                all_keys.update(struct_fields.keys())

    binary_encoding_map = {key: i for i, key in enumerate(all_keys)}
    final_string = "\n".join(all_keys)

    checksum = create_checksum(final_string)
    return BinaryEncoding(binary_encoding_map, checksum)
