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
            union_cases: dict[str, UStruct] = value.cases
            for case_key, case_value in union_cases.items():
                all_keys.add(case_key)
                struct_fields = case_value.fields
                all_keys.update(struct_fields.keys())
        elif isinstance(value, UFn):
            fn_call_cases: dict[str, UStruct] = value.call.cases
            fn_result_cases: dict[str, UStruct] = value.result.cases

            for case_key, case_value in fn_call_cases.items():
                all_keys.add(case_key)
                struct_fields = case_value.fields
                all_keys.update(struct_fields.keys())

            for case_key, case_value in fn_result_cases.items():
                all_keys.add(case_key)
                struct_fields = case_value.fields
                all_keys.update(struct_fields.keys())

    sorted_all_keys = sorted(all_keys)
    binary_encoding = {key: i for i, key in enumerate(sorted_all_keys)}
    final_string = "\n".join(sorted_all_keys)
    checksum = create_checksum(final_string)
    return BinaryEncoding(binary_encoding, checksum)
