import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { UError } from '../../internal/types/UError';
import { UApiSchemaParseError } from '../../UApiSchemaParseError';
import { parseUnionType } from '../../internal/schema/ParseUnionType';
import { ParseContext } from '../../internal/schema/ParseContext';

export function parseErrorType(
    errorDefinitionAsParsedJson: { [key: string]: any },
    schemaKey: string,
    ctx: ParseContext,
): UError {
    const parseFailures: SchemaParseFailure[] = [];

    const otherKeys = Object.keys(errorDefinitionAsParsedJson).filter((key) => key !== schemaKey && key !== '///');

    if (otherKeys.length > 0) {
        for (const k of otherKeys) {
            const loopPath = ctx.path.concat(k);
            parseFailures.push(new SchemaParseFailure(ctx.documentName, loopPath as any[], 'ObjectKeyDisallowed', {}));
        }
    }

    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures);
    }

    const error = parseUnionType(errorDefinitionAsParsedJson, schemaKey, [], [], ctx);

    return new UError(schemaKey, error);
}
