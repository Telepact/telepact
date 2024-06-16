import re from 're';
import { SchemaParseFailure } from 'uapi/internal/schema/SchemaParseFailure';
import { UUnion } from 'uapi/internal/types/UUnion';
import { UApiSchemaParseError } from 'uapi/UApiSchemaParseError';
import { get_type_unexpected_parse_failure } from 'uapi/internal/schema/GetTypeUnexpectedParseFailure';
import { parse_struct_fields } from 'uapi/internal/schema/ParseStructFields';
import { UStruct } from 'uapi/internal/types/UStruct';
import { UType } from 'uapi/internal/types/UType';

export function parse_union_type(
    path: any[],
    union_definition_as_pseudo_json: { [key: string]: any },
    schema_key: string,
    ignore_keys: string[],
    required_keys: string[],
    type_parameter_count: number,
    u_api_schema_pseudo_json: any[],
    schema_keys_to_index: { [key: string]: number },
    parsed_types: { [key: string]: any },
    type_extensions: { [key: string]: any },
    all_parse_failures: SchemaParseFailure[],
    failed_types: Set<string>,
): UUnion {
    const parse_failures: SchemaParseFailure[] = [];

    const other_keys = new Set(Object.keys(union_definition_as_pseudo_json));
    other_keys.delete(schema_key);
    other_keys.delete('///');
    for (const ignore_key of ignore_keys) {
        other_keys.delete(ignore_key);
    }

    if (other_keys.size > 0) {
        for (const k of other_keys) {
            const loop_path = path.concat(k);
            parse_failures.push(new SchemaParseFailure(loop_path, 'ObjectKeyDisallowed', {}, null));
        }
    }

    const this_path = path.concat(schema_key);
    const def_init = union_definition_as_pseudo_json[schema_key];

    if (!Array.isArray(def_init)) {
        const final_parse_failures = get_type_unexpected_parse_failure(this_path, def_init, 'Array');
        parse_failures.push(...final_parse_failures);
        throw new UApiSchemaParseError(parse_failures);
    }

    const definition2 = def_init;
    const definition = [];
    let index = -1;
    for (const element of definition2) {
        index += 1;
        const loop_path = this_path.concat(index);
        if (typeof element !== 'object' || Array.isArray(element)) {
            const this_parse_failures = get_type_unexpected_parse_failure(loop_path, element, 'Object');
            parse_failures.push(...this_parse_failures);
            continue;
        }
        definition.push(element);
    }

    if (parse_failures.length > 0) {
        throw new UApiSchemaParseError(parse_failures);
    }

    if (definition.length === 0 && required_keys.length === 0) {
        parse_failures.push(new SchemaParseFailure(this_path, 'EmptyArrayDisallowed', {}, null));
    } else {
        for (const required_key of required_keys) {
            let found = false;
            for (const element of definition) {
                const case_keys = new Set(Object.keys(element));
                case_keys.delete('///');
                if (case_keys.has(required_key)) {
                    found = true;
                    break;
                }
            }
            if (!found) {
                const branch_path = this_path.concat(0, required_key);
                parse_failures.push(new SchemaParseFailure(branch_path, 'RequiredObjectKeyMissing', {}, null));
            }
        }
    }

    const cases: { [key: string]: UStruct } = {};
    const case_indices: { [key: string]: number } = {};

    for (let i = 0; i < definition.length; i++) {
        const element = definition[i];
        const loop_path = this_path.concat(i);
        const map_init = element;
        const map = Object.fromEntries(map_init);
        delete map['///'];
        const keys = Object.keys(map);

        const regex_string = '^([A-Z][a-zA-Z0-9_]*)$';

        const matches = keys.filter((k) => re.match(regex_string, k));
        if (matches.length !== 1) {
            parse_failures.push(
                new SchemaParseFailure(
                    loop_path,
                    'ObjectKeyRegexMatchCountUnexpected',
                    { regex: regex_string, actual: matches.length, expected: 1, keys: keys },
                    null,
                ),
            );
            continue;
        }
        if (Object.keys(map).length !== 1) {
            parse_failures.push(
                new SchemaParseFailure(
                    loop_path,
                    'ObjectSizeUnexpected',
                    { expected: 1, actual: Object.keys(map).length },
                    null,
                ),
            );
            continue;
        }

        const entry = Object.entries(map)[0];
        const union_case = entry[0];
        const union_key_path = loop_path.concat(union_case);

        if (typeof entry[1] !== 'object' || Array.isArray(entry[1])) {
            const this_parse_failures = get_type_unexpected_parse_failure(union_key_path, entry[1], 'Object');
            parse_failures.push(...this_parse_failures);
            continue;
        }
        const union_case_struct = entry[1];

        try {
            const fields = parse_struct_fields(
                union_case_struct,
                union_key_path,
                type_parameter_count,
                u_api_schema_pseudo_json,
                schema_keys_to_index,
                parsed_types,
                type_extensions,
                all_parse_failures,
                failed_types,
            );
            const union_struct = new UStruct(`${schema_key}.${union_case}`, fields, type_parameter_count);
            cases[union_case] = union_struct;
            case_indices[union_case] = i;
        } catch (e) {
            if (e instanceof UApiSchemaParseError) {
                parse_failures.push(...e.schema_parse_failures);
            }
        }
    }

    if (parse_failures.length > 0) {
        throw new UApiSchemaParseError(parse_failures);
    }

    return new UUnion(schema_key, cases, case_indices, type_parameter_count);
}
