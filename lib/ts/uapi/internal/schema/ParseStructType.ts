import { SchemaParseFailure } from 'uapi/internal/schema/SchemaParseFailure';
import { UStruct } from 'uapi/internal/types/UStruct';
import { UType } from 'uapi/internal/types/UType';
import { get_type_unexpected_parse_failure } from 'uapi/internal/schema/GetTypeUnexpectedParseFailure';
import { parse_struct_fields } from 'uapi/internal/schema/ParseStructFields';
import { UApiSchemaParseError } from 'uapi/UApiSchemaParseError';

export function parse_struct_type(
    path: any[],
    struct_definition_as_pseudo_json: { [key: string]: any },
    schema_key: string,
    ignore_keys: string[],
    type_parameter_count: number,
    uapi_schema_pseudo_json: any[],
    schema_keys_to_index: { [key: string]: number },
    parsed_types: { [key: string]: UType },
    type_extensions: { [key: string]: UType },
    all_parse_failures: SchemaParseFailure[],
    failed_types: Set<string>,
): UStruct {
    const parse_failures: SchemaParseFailure[] = [];
    const other_keys = new Set(Object.keys(struct_definition_as_pseudo_json));

    other_keys.delete(schema_key);
    other_keys.delete('///');
    other_keys.delete('_ignoreIfDuplicate');
    for (const ignore_key of ignore_keys) {
        other_keys.delete(ignore_key);
    }

    if (other_keys.size > 0) {
        for (const k of other_keys) {
            const loop_path = [...path, k];
            parse_failures.push(new SchemaParseFailure(loop_path, 'ObjectKeyDisallowed', {}, null));
        }
    }

    const this_path = [...path, schema_key];
    const def_init = struct_definition_as_pseudo_json[schema_key];

    let definition: { [key: string]: any } | null = null;
    if (typeof def_init !== 'object' || def_init === null) {
        const branch_parse_failures = get_type_unexpected_parse_failure(this_path, def_init, 'Object');
        parse_failures.push(...branch_parse_failures);
    } else {
        definition = def_init;
    }

    if (parse_failures.length > 0) {
        throw new UApiSchemaParseError(parse_failures);
    }

    const fields = parse_struct_fields(
        definition,
        this_path,
        type_parameter_count,
        uapi_schema_pseudo_json,
        schema_keys_to_index,
        parsed_types,
        type_extensions,
        all_parse_failures,
        failed_types,
    );

    return new UStruct(schema_key, fields, type_parameter_count);
}
