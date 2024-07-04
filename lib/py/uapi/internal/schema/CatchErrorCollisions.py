from typing import cast


def catch_error_collisions(u_api_schema_pseudo_json: list[object], error_keys: set[str], keys_to_index: dict[str, int]) -> None:
    from uapi.UApiSchemaParseError import UApiSchemaParseError
    from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure

    parse_failures = []

    indices = sorted([keys_to_index[key] for key in error_keys])
    index_to_keys = {v: k for k, v in keys_to_index.items()}

    for i in range(len(indices)):
        for j in range(i + 1, len(indices)):
            index = indices[i]
            other_index = indices[j]

            def_ = cast(dict[str, object], u_api_schema_pseudo_json[index])
            other_def = cast(dict[str, object],
                             u_api_schema_pseudo_json[other_index])

            def_key = index_to_keys[index]
            other_def_key = index_to_keys[other_index]

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
                            [other_index, other_def_key, l,
                                this_other_error_def_key],
                            "PathCollision",
                            {"other": [index, def_key,
                                       k, this_error_def_key]},
                            other_def_key
                        ))

    if parse_failures:
        raise UApiSchemaParseError(parse_failures)
