import { UApiSchemaParseError } from '../../UApiSchemaParseError';
import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';

export function findSchemaKey(documentName: string, definition: Record<string, any>, index: number): string {
    const regex = /^(((fn|errors|requestHeader|responseHeader|info)|((struct|union|_ext)(<[0-2]>)?))\..*)/;
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
        const parseFailure = new SchemaParseFailure(documentName, [index], 'ObjectKeyRegexMatchCountUnexpected', {
            regex: regex.toString().slice(1, -1),
            actual: matches.length,
            expected: 1,
            keys: keys,
        });
        throw new UApiSchemaParseError([parseFailure]);
    }
}
