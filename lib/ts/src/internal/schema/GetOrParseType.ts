import { UApiSchemaParseError } from '../../UApiSchemaParseError';
import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { UType } from '../../internal/types/UType';
import { UObject } from '../../internal/types/UObject';
import { UArray } from '../../internal/types/UArray';
import { UBoolean } from '../../internal/types/UBoolean';
import { UInteger } from '../../internal/types/UInteger';
import { UNumber } from '../../internal/types/UNumber';
import { UString } from '../../internal/types/UString';
import { UAny } from '../../internal/types/UAny';
import { parseFunctionType } from '../../internal/schema/ParseFunctionType';
import { parseStructType } from '../../internal/schema/ParseStructType';
import { parseUnionType } from '../../internal/schema/ParseUnionType';
import { USelect } from '../../internal/types/USelect';
import { UMockCall } from '../../internal/types/UMockCall';
import { UMockStub } from '../../internal/types/UMockStub';
import { ParseContext } from '../../internal/schema/ParseContext';

export function getOrParseType(typeName: string, ctx: ParseContext): UType {
    if (ctx.failedTypes.has(typeName)) {
        throw new UApiSchemaParseError([], ctx.uapiSchemaDocumentNamesToJson);
    }

    const existingType = ctx.parsedTypes[typeName];
    if (existingType !== undefined) {
        return existingType;
    }

    const regexString = `^(boolean|integer|number|string|any|array|object)|((fn|(union|struct|_ext))\\.([a-zA-Z_]\\w*))$`;
    const regex = new RegExp(regexString);

    const matcher = typeName.match(regex);
    if (!matcher) {
        throw new UApiSchemaParseError(
            [new SchemaParseFailure(ctx.documentName, ctx.path, 'StringRegexMatchFailed', { regex: regexString })],
            ctx.uapiSchemaDocumentNamesToJson,
        );
    }

    const standardTypeName = matcher[1];
    if (standardTypeName) {
        return (
            {
                boolean: new UBoolean(),
                integer: new UInteger(),
                number: new UNumber(),
                string: new UString(),
                array: new UArray(),
                object: new UObject(),
            }[standardTypeName] || new UAny()
        );
    }

    const customTypeName = matcher[2];
    const thisIndex = ctx.schemaKeysToIndex[customTypeName];
    const thisDocumentName = ctx.schemaKeysToDocumentName[customTypeName];
    if (thisIndex === undefined) {
        throw new UApiSchemaParseError(
            [new SchemaParseFailure(ctx.documentName, ctx.path, 'TypeUnknown', { name: customTypeName })],
            ctx.uapiSchemaDocumentNamesToJson,
        );
    }
    const definition = ctx.uapiSchemaDocumentNamesToPseudoJson[thisDocumentName][thisIndex] as {
        [key: string]: object;
    };

    let type: UType;
    try {
        if (customTypeName.startsWith('struct')) {
            type = parseStructType(
                definition,
                customTypeName,
                [],
                ctx.copy({ documentName: thisDocumentName, path: [thisIndex] }),
            );
        } else if (customTypeName.startsWith('union')) {
            type = parseUnionType(
                definition,
                customTypeName,
                [],
                [],
                ctx.copy({ documentName: thisDocumentName, path: [thisIndex] }),
            );
        } else if (customTypeName.startsWith('fn')) {
            type = parseFunctionType(
                definition,
                customTypeName,
                ctx.copy({ documentName: thisDocumentName, path: [thisIndex] }),
            );
        } else {
            const possibleTypeExtension = {
                '_ext.Select_': new USelect(ctx.parsedTypes),
                '_ext.Call_': new UMockCall(ctx.parsedTypes),
                '_ext.Stub_': new UMockStub(ctx.parsedTypes),
            }[customTypeName];
            if (!possibleTypeExtension) {
                throw new UApiSchemaParseError(
                    [
                        new SchemaParseFailure(ctx.documentName, [thisIndex], 'TypeExtensionImplementationMissing', {
                            name: customTypeName,
                        }),
                    ],
                    ctx.uapiSchemaDocumentNamesToJson,
                );
            }
            type = possibleTypeExtension;
        }

        ctx.parsedTypes[customTypeName] = type;

        return type;
    } catch (e) {
        if (e instanceof UApiSchemaParseError) {
            ctx.allParseFailures.push(...e.schemaParseFailures);
            ctx.failedTypes.add(customTypeName);
            throw new UApiSchemaParseError([], ctx.uapiSchemaDocumentNamesToJson);
        }
        throw e;
    }
}
