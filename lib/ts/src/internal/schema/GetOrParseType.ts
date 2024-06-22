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

export function getOrParseType(
    path: any[],
    typeName: string,
    thisTypeParameterCount: number,
    uApiSchemaPseudoJson: object[],
    schemaKeysToIndex: { [key: string]: number },
    parsedTypes: { [key: string]: UType },
    typeExtensions: { [key: string]: UType },
    allParseFailures: SchemaParseFailure[],
    failedTypes: Set<string>,
): UType {
    if (typeName in failedTypes) {
        throw new UApiSchemaParseError([]);
    }

    const existingType = parsedTypes[typeName];
    if (existingType) {
        return existingType;
    }

    const genericRegex =
        thisTypeParameterCount > 0
            ? `|(T.([0-${thisTypeParameterCount - 1}]${thisTypeParameterCount > 1 ? '' : '0'})`
            : '';

    const regexString = `^(boolean|integer|number|string|any|array|object)|((fn|(union|struct|_ext)(<([1-3])>)?)\\.([a-zA-Z_]\\w*)${genericRegex})$`;
    const regex = new RegExp(regexString);

    const matcher = typeName.match(regex);
    if (!matcher) {
        throw new UApiSchemaParseError([
            new SchemaParseFailure(path, 'StringRegexMatchFailed', { regex: regexString }, null),
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
        if (genericParameterIndexString) {
            const genericParameterIndex = parseInt(genericParameterIndexString);
            return new UGeneric(genericParameterIndex);
        }
    }

    const customTypeName = matcher[2];
    const index = schemaKeysToIndex[customTypeName];
    if (index === undefined) {
        throw new UApiSchemaParseError([new SchemaParseFailure(path, 'TypeUnknown', { name: customTypeName }, null)]);
    }
    const definition = uApiSchemaPseudoJson[index] as { [key: string]: object };

    const typeParameterCountString = matcher[6];
    const typeParameterCount = typeParameterCountString ? parseInt(typeParameterCountString) : 0;

    let type: UType;
    try {
        if (customTypeName.startsWith('struct')) {
            type = parseStructType(
                [index],
                definition,
                customTypeName,
                [],
                typeParameterCount,
                uApiSchemaPseudoJson,
                schemaKeysToIndex,
                parsedTypes,
                typeExtensions,
                allParseFailures,
                failedTypes,
            );
        } else if (customTypeName.startsWith('union')) {
            type = parseUnionType(
                [index],
                definition,
                customTypeName,
                [],
                [],
                typeParameterCount,
                uApiSchemaPseudoJson,
                schemaKeysToIndex,
                parsedTypes,
                typeExtensions,
                allParseFailures,
                failedTypes,
            );
        } else if (customTypeName.startsWith('fn')) {
            type = parseFunctionType(
                [index],
                definition,
                customTypeName,
                uApiSchemaPseudoJson,
                schemaKeysToIndex,
                parsedTypes,
                typeExtensions,
                allParseFailures,
                failedTypes,
            );
        } else {
            const possibleType = typeExtensions[customTypeName];
            if (!possibleType) {
                throw new UApiSchemaParseError([
                    new SchemaParseFailure(
                        [index],
                        'TypeExtensionImplementationMissing',
                        { name: customTypeName },
                        null,
                    ),
                ]);
            }
            type = possibleType;
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
