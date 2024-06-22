import { UApiSchemaParseError } from '../../UApiSchemaParseError';
import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';

export function findSchemaKey(definition: Record<string, any>, index: number): string {
    const regex = /^(errors|((fn|requestHeader|responseHeader|info)|((struct|union|_ext)(<[0-2]>)?))\..*)/;
    const matches: string[] = [];

    const keys = Object.keys(definition).sort();

    for (const e of keys) {
        if (regex.test(e)) {
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
                regex: regex.toString(),
                actual: matches.length,
                expected: 1,
                keys: keys,
            },
            null,
        );
        throw new UApiSchemaParseError([parseFailure]);
    }
}
