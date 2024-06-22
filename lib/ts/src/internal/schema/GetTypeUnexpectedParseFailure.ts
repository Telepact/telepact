import { SchemaParseFailure } from 'uapi/internal/schema/SchemaParseFailure';
import { getType } from 'uapi/internal/types/GetType';

export function getTypeUnexpectedParseFailure(path: any[], value: any, expectedType: string): SchemaParseFailure[] {
    const actualType = getType(value);
    const data: { actual: { [key: string]: any }; expected: { [key: string]: any } } = {
        actual: { [actualType]: {} },
        expected: { [expectedType]: {} },
    };
    return [new SchemaParseFailure(path, 'TypeUnexpected', data, null)];
}
