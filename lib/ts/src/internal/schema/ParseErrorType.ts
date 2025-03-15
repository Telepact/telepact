import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { VError } from '../types/VError';
import { MsgPactSchemaParseError } from '../../MsgPactSchemaParseError';
import { parseUnionType } from '../../internal/schema/ParseUnionType';
import { ParseContext } from '../../internal/schema/ParseContext';

export function parseErrorType(
    path: any[],
    errorDefinitionAsParsedJson: { [key: string]: any },
    schemaKey: string,
    ctx: ParseContext,
): VError {
    const parseFailures: SchemaParseFailure[] = [];

    const otherKeys = Object.keys(errorDefinitionAsParsedJson).filter((key) => key !== schemaKey && key !== '///');

    if (otherKeys.length > 0) {
        for (const k of otherKeys) {
            const loopPath = path.concat(k);
            parseFailures.push(new SchemaParseFailure(ctx.documentName, loopPath as any[], 'ObjectKeyDisallowed', {}));
        }
    }

    if (parseFailures.length > 0) {
        throw new MsgPactSchemaParseError(parseFailures, ctx.msgpactSchemaDocumentNamesToJson);
    }

    const error = parseUnionType(path, errorDefinitionAsParsedJson, schemaKey, [], [], ctx);

    return new VError(schemaKey, error);
}
