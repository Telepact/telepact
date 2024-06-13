from typing import cast


def catch_error_collisions(u_api_schema_pseudo_json: list[object], error_indices: set[int], keys_to_index: dict[str, int]) -> None:
    from uapi.UApiSchemaParseError import UApiSchemaParseError
    from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure

    parse_failures = []

    indices = sorted(error_indices)

    for i in range(len(indices)):
        for j in range(i + 1, len(indices)):
            index = indices[i]
            other_index = indices[j]

            def_ = cast(dict[str, object], u_api_schema_pseudo_json[index])
            other_def = cast(dict[str, object],
                             u_api_schema_pseudo_json[other_index])

            err_def = cast(list[object], def_["errors"])
            other_err_def = cast(list[object], other_def["errors"])

            for k in range(len(err_def)):
                this_err_def = cast(dict[str, object], err_def[k])
                this_err_def_keys = set(this_err_def.keys())
                this_err_def_keys.remove("///")

                for l in range(len(other_err_def)):
                    this_other_err_def = cast(
                        dict[str, object], other_err_def[l])
                    this_other_err_def_keys = set(this_other_err_def.keys())
                    this_other_err_def_keys.remove("///")

                    if this_err_def_keys == this_other_err_def_keys:
                        this_error_def_key = next(iter(this_err_def_keys))
                        this_other_error_def_key = next(
                            iter(this_other_err_def_keys))
                        parse_failures.append(SchemaParseFailure(
                            [other_index, "errors", l, this_other_error_def_key],
                            "PathCollision",
                            {"other": [index, "errors",
                                       k, this_error_def_key]},
                            "errors"
                        ))

    if parse_failures:
        raise UApiSchemaParseError(parse_failures)
