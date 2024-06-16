import { UApiSchemaParseError } from 'uapi/UApiSchemaParseError';
import { SchemaParseFailure } from 'uapi/internal/schema/SchemaParseFailure';
import * as re from 're';

export function findSchemaKey(definition: Record<string, any>, index: number): string {
    const regex = '^(errors|((fn|requestHeader|responseHeader|info)|((struct|union|_ext)(<[0-2]>)?))\\..*)';
    const matches: string[] = [];

    const keys = Object.keys(definition).sort();

    for (const e of keys) {
        if (re.match(regex, e)) {
            matches.push(e);
        }
    }

    if (matches.length === 1) {
        return matches[0];
    } else {
        const parseFailure = new SchemaParseFailure(
            [index],
            'ObjectKeyRegexMatchCountUnexpected',
            {
                regex: regex,
                actual: matches.length,
                expected: 1,
                keys: keys,
            },
            null,
        );
        throw new UApiSchemaParseError([parseFailure]);
    }
}
