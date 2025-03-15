import { MsgPactSchemaParseError } from '../../MsgPactSchemaParseError';
import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { VType } from '../types/VType';
import { VObject } from '../types/VObject';
import { VArray } from '../types/VArray';
import { VBoolean } from '../types/VBoolean';
import { VInteger } from '../types/VInteger';
import { VNumber } from '../types/VNumber';
import { VString } from '../types/VString';
import { VAny } from '../types/VAny';
import { parseFunctionType } from '../../internal/schema/ParseFunctionType';
import { parseStructType } from '../../internal/schema/ParseStructType';
import { parseUnionType } from '../../internal/schema/ParseUnionType';
import { VSelect } from '../types/VSelect';
import { VMockCall } from '../types/VMockCall';
import { VMockStub } from '../types/VMockStub';
import { ParseContext } from '../../internal/schema/ParseContext';

export function getOrParseType(path: any[], typeName: string, ctx: ParseContext): VType {
    if (ctx.failedTypes.has(typeName)) {
        throw new MsgPactSchemaParseError([], ctx.msgpactSchemaDocumentNamesToJson);
    }

    const existingType = ctx.parsedTypes[typeName];
    if (existingType !== undefined) {
        return existingType;
    }

    const regexString = `^(boolean|integer|number|string|any|array|object)|((fn|(union|struct|_ext))\\.([a-zA-Z_]\\w*))$`;
    const regex = new RegExp(regexString);

    const matcher = typeName.match(regex);
    if (!matcher) {
        throw new MsgPactSchemaParseError(
            [new SchemaParseFailure(ctx.documentName, path, 'StringRegexMatchFailed', { regex: regexString })],
            ctx.msgpactSchemaDocumentNamesToJson,
        );
    }

    const standardTypeName = matcher[1];
    if (standardTypeName) {
        return (
            {
                boolean: new VBoolean(),
                integer: new VInteger(),
                number: new VNumber(),
                string: new VString(),
                array: new VArray(),
                object: new VObject(),
            }[standardTypeName] || new VAny()
        );
    }

    const customTypeName = matcher[2];
    const thisIndex = ctx.schemaKeysToIndex[customTypeName];
    const thisDocumentName = ctx.schemaKeysToDocumentName[customTypeName];
    if (thisIndex === undefined) {
        throw new MsgPactSchemaParseError(
            [new SchemaParseFailure(ctx.documentName, path, 'TypeUnknown', { name: customTypeName })],
            ctx.msgpactSchemaDocumentNamesToJson,
        );
    }
    const definition = ctx.msgpactSchemaDocumentNamesToPseudoJson[thisDocumentName][thisIndex] as {
        [key: string]: object;
    };

    let type: VType;
    try {
        if (customTypeName.startsWith('struct')) {
            type = parseStructType(
                [thisIndex],
                definition,
                customTypeName,
                [],
                ctx.copy({ documentName: thisDocumentName }),
            );
        } else if (customTypeName.startsWith('union')) {
            type = parseUnionType(
                [thisIndex],
                definition,
                customTypeName,
                [],
                [],
                ctx.copy({ documentName: thisDocumentName }),
            );
        } else if (customTypeName.startsWith('fn')) {
            type = parseFunctionType(
                [thisIndex],
                definition,
                customTypeName,
                ctx.copy({ documentName: thisDocumentName }),
            );
        } else {
            const possibleTypeExtension = {
                '_ext.Select_': new VSelect(),
                '_ext.Call_': new VMockCall(ctx.parsedTypes),
                '_ext.Stub_': new VMockStub(ctx.parsedTypes),
            }[customTypeName];
            if (!possibleTypeExtension) {
                throw new MsgPactSchemaParseError(
                    [
                        new SchemaParseFailure(ctx.documentName, [thisIndex], 'TypeExtensionImplementationMissing', {
                            name: customTypeName,
                        }),
                    ],
                    ctx.msgpactSchemaDocumentNamesToJson,
                );
            }
            type = possibleTypeExtension;
        }

        ctx.parsedTypes[customTypeName] = type;

        return type;
    } catch (e) {
        if (e instanceof MsgPactSchemaParseError) {
            ctx.allParseFailures.push(...e.schemaParseFailures);
            ctx.failedTypes.add(customTypeName);
            throw new MsgPactSchemaParseError([], ctx.msgpactSchemaDocumentNamesToJson);
        }
        throw e;
    }
}
