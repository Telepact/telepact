from typing import cast


def catch_error_collisions(u_api_schema_name_to_pseudo_json: dict[str, list[object]], error_keys: set[str], keys_to_index: dict[str, int], schema_keys_to_document_name: dict[str, str]) -> None:
    from uapi.UApiSchemaParseError import UApiSchemaParseError
    from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure

    parse_failures = []
    error_keys_list = list(error_keys)
    error_keys_list.sort(key=lambda k: keys_to_index[k])

    indices = sorted([keys_to_index[key] for key in error_keys])
    index_to_keys = {v: k for k, v in keys_to_index.items()}

    for i in range(len(error_keys_list)):
        for j in range(i + 1, len(error_keys_list)):
            def_key = error_keys_list[i]
            other_def_key = error_keys_list[j]

            index = keys_to_index[def_key]
            other_index = keys_to_index[other_def_key]

            document_name = schema_keys_to_document_name[def_key]
            other_document_name = schema_keys_to_document_name[other_def_key]

            u_api_schema_pseudo_json = u_api_schema_name_to_pseudo_json[document_name]
            other_u_api_schema_pseudo_json = u_api_schema_name_to_pseudo_json[other_document_name]

            def_ = cast(dict[str, object], u_api_schema_pseudo_json[index])
            other_def = cast(dict[str, object],
                             other_u_api_schema_pseudo_json[other_index])

            err_def = cast(list[object], def_[def_key])
            other_err_def = cast(list[object], other_def[other_def_key])

            for k in range(len(err_def)):
                this_err_def = cast(dict[str, object], err_def[k])
                this_err_def_keys = set(this_err_def.keys())
                this_err_def_keys.discard("///")

                for l in range(len(other_err_def)):
                    this_other_err_def = cast(
                        dict[str, object], other_err_def[l])
                    this_other_err_def_keys = set(this_other_err_def.keys())
                    this_other_err_def_keys.discard("///")

                    if this_err_def_keys == this_other_err_def_keys:
                        this_error_def_key = next(iter(this_err_def_keys))
                        this_other_error_def_key = next(
                            iter(this_other_err_def_keys))
                        parse_failures.append(SchemaParseFailure(
                            other_document_name,
                            [other_index, other_def_key, l,
                                this_other_error_def_key],
                            "PathCollision",
                            {"document": document_name,
                             "path": [index, def_key, k, this_error_def_key]}
                        ))

    if parse_failures:
        raise UApiSchemaParseError(parse_failures)
