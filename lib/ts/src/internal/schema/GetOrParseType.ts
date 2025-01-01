import { UApiSchemaParseError } from '../../UApiSchemaParseError';
import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { UType } from '../../internal/types/UType';
import { UObject } from '../../internal/types/UObject';
import { UArray } from '../../internal/types/UArray';
import { UBoolean } from '../../internal/types/UBoolean';
import { UGeneric } from '../../internal/types/UGeneric';
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

export function getOrParseType(
    documentName: string,
    path: any[],
    typeName: string,
    thisTypeParameterCount: number,
    uApiSchemaDocumentNameToPseudoJson: { [key: string]: object[] },
    schemaKeysToDocumentNames: { [key: string]: string },
    schemaKeysToIndex: { [key: string]: number },
    parsedTypes: { [key: string]: UType },
    allParseFailures: SchemaParseFailure[],
    failedTypes: Set<string>,
): UType {
    if (failedTypes.has(typeName)) {
        throw new UApiSchemaParseError([]);
    }

    const existingType = parsedTypes[typeName];
    if (existingType !== undefined) {
        return existingType;
    }

    let genericRegex: string;
    if (thisTypeParameterCount > 0) {
        genericRegex = `|(T([%s]))`.replace(
            '%s',
            thisTypeParameterCount > 1 ? '0-%d'.replace('%d', String(thisTypeParameterCount - 1)) : '0',
        );
    } else {
        genericRegex = '';
    }

    const regexString = `^(boolean|integer|number|string|any|array|object)|((fn|(union|struct|_ext)(<([1-3])>)?)\\.([a-zA-Z_]\\w*)${genericRegex})$`;
    const regex = new RegExp(regexString);

    const matcher = typeName.match(regex);
    if (!matcher) {
        throw new UApiSchemaParseError([
            new SchemaParseFailure(documentName, path, 'StringRegexMatchFailed', { regex: regexString }),
        ]);
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

    if (thisTypeParameterCount > 0) {
        const genericParameterIndexString = matcher[9];
        if (genericParameterIndexString !== undefined) {
            const genericParameterIndex = parseInt(genericParameterIndexString);
            return new UGeneric(genericParameterIndex);
        }
    }

    const customTypeName = matcher[2];
    const thisIndex = schemaKeysToIndex[customTypeName];
    const thisDocumentName = schemaKeysToDocumentNames[customTypeName];
    if (thisIndex === undefined) {
        throw new UApiSchemaParseError([
            new SchemaParseFailure(documentName, path, 'TypeUnknown', { name: customTypeName }),
        ]);
    }
    const definition = uApiSchemaDocumentNameToPseudoJson[thisDocumentName][thisIndex] as { [key: string]: object };

    const typeParameterCountString = matcher[6];
    const typeParameterCount = typeParameterCountString ? parseInt(typeParameterCountString) : 0;

    let type: UType;
    try {
        if (customTypeName.startsWith('struct')) {
            type = parseStructType(
                thisDocumentName,
                [thisIndex],
                definition,
                customTypeName,
                [],
                typeParameterCount,
                uApiSchemaDocumentNameToPseudoJson,
                schemaKeysToDocumentNames,
                schemaKeysToIndex,
                parsedTypes,
                allParseFailures,
                failedTypes,
            );
        } else if (customTypeName.startsWith('union')) {
            type = parseUnionType(
                thisDocumentName,
                [thisIndex],
                definition,
                customTypeName,
                [],
                [],
                typeParameterCount,
                uApiSchemaDocumentNameToPseudoJson,
                schemaKeysToDocumentNames,
                schemaKeysToIndex,
                parsedTypes,
                allParseFailures,
                failedTypes,
            );
        } else if (customTypeName.startsWith('fn')) {
            type = parseFunctionType(
                thisDocumentName,
                [thisIndex],
                definition,
                customTypeName,
                uApiSchemaDocumentNameToPseudoJson,
                schemaKeysToDocumentNames,
                schemaKeysToIndex,
                parsedTypes,
                allParseFailures,
                failedTypes,
            );
        } else {
            const possibleTypeExtension = {
                '_ext.Select_': new USelect(parsedTypes),
                '_ext.Call_': new UMockCall(parsedTypes),
                '_ext.Stub_': new UMockStub(parsedTypes),
            }[customTypeName];
            if (!possibleTypeExtension) {
                throw new UApiSchemaParseError([
                    new SchemaParseFailure(documentName, [thisIndex], 'TypeExtensionImplementationMissing', {
                        name: customTypeName,
                    }),
                ]);
            }
            type = possibleTypeExtension;
        }

        parsedTypes[customTypeName] = type;

        return type;
    } catch (e) {
        if (e instanceof UApiSchemaParseError) {
            allParseFailures.push(...e.schemaParseFailures);
            failedTypes.add(customTypeName);
            throw new UApiSchemaParseError([]);
        }
        throw e;
    }
}
