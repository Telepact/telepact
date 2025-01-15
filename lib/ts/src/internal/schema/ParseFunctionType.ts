import { UFn } from '../../internal/types/UFn';
import { UUnion } from '../../internal/types/UUnion';
import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { getTypeUnexpectedParseFailure } from '../../internal/schema/GetTypeUnexpectedParseFailure';
import { parseStructType } from '../../internal/schema/ParseStructType';
import { parseUnionType } from '../../internal/schema/ParseUnionType';
import { UApiSchemaParseError } from '../../UApiSchemaParseError';
import { ParseContext } from '../../internal/schema/ParseContext';

export function parseFunctionType(
    functionDefinitionAsParsedJson: { [key: string]: any },
    schemaKey: string,
    ctx: ParseContext,
): UFn {
    const parseFailures: SchemaParseFailure[] = [];

    let callType: UUnion | null = null;
    try {
        const argType = parseStructType(functionDefinitionAsParsedJson, schemaKey, ['->', '_errors'], ctx);
        callType = new UUnion(schemaKey, { [schemaKey]: argType }, { [schemaKey]: 0 });
    } catch (e) {
        if (e instanceof UApiSchemaParseError) {
            parseFailures.push(...e.schemaParseFailures);
        } else {
            throw e;
        }
    }

    const resultSchemaKey = '->';

    const resPath = [...ctx.path, resultSchemaKey];

    let resultType: UUnion | null = null;
    if (!(resultSchemaKey in functionDefinitionAsParsedJson)) {
        parseFailures.push(new SchemaParseFailure(ctx.documentName, resPath, 'RequiredObjectKeyMissing', {}));
    } else {
        try {
            resultType = parseUnionType(
                functionDefinitionAsParsedJson,
                resultSchemaKey,
                Object.keys(functionDefinitionAsParsedJson),
                ['Ok_'],
                ctx,
            );
        } catch (e) {
            if (e instanceof UApiSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            } else {
                throw e;
            }
        }
    }

    const errorsRegexKey = '_errors';

    const regexPath = [...ctx.path, errorsRegexKey];

    let errorsRegex: string | null = null;
    if (errorsRegexKey in functionDefinitionAsParsedJson && !schemaKey.endsWith('_')) {
        parseFailures.push(new SchemaParseFailure(ctx.documentName, regexPath, 'ObjectKeyDisallowed', {}));
    } else {
        const errorsRegexInit =
            errorsRegexKey in functionDefinitionAsParsedJson
                ? functionDefinitionAsParsedJson[errorsRegexKey]
                : '^errors\\..*$';

        if (typeof errorsRegexInit !== 'string') {
            const thisParseFailures = getTypeUnexpectedParseFailure(
                ctx.documentName,
                regexPath,
                errorsRegexInit,
                'String',
            );
            parseFailures.push(...thisParseFailures);
        } else {
            errorsRegex = errorsRegexInit;
        }
    }

    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures, ctx.uapiSchemaDocumentNamesToJson);
    }

    return new UFn(schemaKey, callType as UUnion, resultType as UUnion, errorsRegex as string);
}
