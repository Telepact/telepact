import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { VStruct } from '../types/VStruct';
import { getTypeUnexpectedParseFailure } from '../../internal/schema/GetTypeUnexpectedParseFailure';
import { parseStructFields } from '../../internal/schema/ParseStructFields';
import { MsgPactSchemaParseError } from '../../MsgPactSchemaParseError';
import { ParseContext } from '../../internal/schema/ParseContext';

export function parseStructType(
    path: any[],
    structDefinitionAsPseudoJson: { [key: string]: any },
    schemaKey: string,
    ignoreKeys: string[],
    ctx: ParseContext,
): VStruct {
    const parseFailures: SchemaParseFailure[] = [];
    const otherKeys = new Set(Object.keys(structDefinitionAsPseudoJson));

    otherKeys.delete(schemaKey);
    otherKeys.delete('///');
    otherKeys.delete('_ignoreIfDuplicate');
    for (const ignoreKey of ignoreKeys) {
        otherKeys.delete(ignoreKey);
    }

    if (otherKeys.size > 0) {
        for (const k of otherKeys) {
            const loopPath = [...path, k];
            parseFailures.push(new SchemaParseFailure(ctx.documentName, loopPath, 'ObjectKeyDisallowed', {}));
        }
    }

    const thisPath = [...path, schemaKey];
    const defInit = structDefinitionAsPseudoJson[schemaKey];

    let definition: { [key: string]: any } | null = null;
    if (typeof defInit !== 'object' || Array.isArray(defInit) || defInit === null || defInit === undefined) {
        const branchParseFailures = getTypeUnexpectedParseFailure(ctx.documentName, thisPath, defInit, 'Object');
        parseFailures.push(...branchParseFailures);
    } else {
        definition = defInit;
    }

    if (parseFailures.length > 0) {
        throw new MsgPactSchemaParseError(parseFailures, ctx.msgpactSchemaDocumentNamesToJson);
    }

    const fields = parseStructFields(thisPath, definition, ctx);

    return new VStruct(schemaKey, fields);
}
