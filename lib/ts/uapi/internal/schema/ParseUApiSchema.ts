import { UApiSchema } from 'uapi/UApiSchema';
import { SchemaParseFailure } from 'uapi/internal/schema/SchemaParseFailure';
import { UType } from 'uapi/internal/types/UType';
import { UFieldDeclaration } from 'uapi/internal/types/UFieldDeclaration';
import { UApiSchemaParseError } from 'uapi/UApiSchemaParseError';
import { applyErrorToParsedTypes } from 'uapi/internal/schema/ApplyErrorToParsedTypes';
import { catchErrorCollisions } from 'uapi/internal/schema/CatchErrorCollisions';
import { findMatchingSchemaKey } from 'uapi/internal/schema/FindMatchingSchemaKey';
import { findSchemaKey } from 'uapi/internal/schema/FindSchemaKey';
import { getOrParseType } from 'uapi/internal/schema/GetOrParseType';
import { getTypeUnexpectedParseFailure } from 'uapi/internal/schema/GetTypeUnexpectedParseFailure';
import { offsetSchemaIndex } from 'uapi/internal/schema/OffsetSchemaIndex';
import { parseErrorType } from 'uapi/internal/schema/ParseErrorType';
import { parseHeadersType } from 'uapi/internal/schema/ParseHeadersType';

export function parseUapiSchema(
    uApiSchemaPseudoJson: any[],
    typeExtensions: { [key: string]: any },
    pathOffset: number,
): UApiSchema {
    const parsedTypes: { [key: string]: any } = {};
    const parseFailures: SchemaParseFailure[] = [];
    const failedTypes: Set<string> = new Set();
    const schemaKeysToIndex: { [key: string]: number } = {};
    const schemaKeys: Set<string> = new Set();
    const errorIndices: Set<number> = new Set();

    let index = -1;
    for (const definition of uApiSchemaPseudoJson) {
        index += 1;
        const loopPath = [index];

        if (typeof definition !== 'object') {
            const thisParseFailures = getTypeUnexpectedParseFailure(loopPath as any[], definition, 'Object');
            parseFailures.push(...thisParseFailures);
            continue;
        }

        const def_ = definition;

        try {
            const schemaKey = findSchemaKey(def_, index);
            if (schemaKey === 'errors') {
                errorIndices.add(index);
                continue;
            }

            const ignoreIfDuplicate = def_['_ignoreIfDuplicate'] || false;
            const matchingSchemaKey = findMatchingSchemaKey(schemaKeys, schemaKey);
            if (matchingSchemaKey !== null) {
                if (!ignoreIfDuplicate) {
                    const otherPathIndex = schemaKeysToIndex[matchingSchemaKey];
                    const finalPath = [...loopPath, schemaKey];
                    parseFailures.push(
                        new SchemaParseFailure(
                            finalPath as any[],
                            'PathCollision',
                            { other: [otherPathIndex, matchingSchemaKey] },
                            schemaKey,
                        ),
                    );
                }
                continue;
            }

            schemaKeys.add(schemaKey);
            schemaKeysToIndex[schemaKey] = index;
        } catch (e) {
            if (e instanceof UApiSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            }
        }
    }

    if (parseFailures.length > 0) {
        const offsetParseFailures = offsetSchemaIndex(parseFailures, pathOffset, schemaKeysToIndex, errorIndices);
        throw new UApiSchemaParseError(offsetParseFailures);
    }

    const requestHeaderKeys: Set<string> = new Set();
    const responseHeaderKeys: Set<string> = new Set();
    const rootTypeParameterCount = 0;

    for (const schemaKey of schemaKeys) {
        if (schemaKey.startsWith('info.')) {
            continue;
        } else if (schemaKey.startsWith('requestHeader.')) {
            requestHeaderKeys.add(schemaKey);
            continue;
        } else if (schemaKey.startsWith('responseHeader.')) {
            responseHeaderKeys.add(schemaKey);
            continue;
        }

        const thisIndex = schemaKeysToIndex[schemaKey];

        try {
            getOrParseType(
                [thisIndex],
                schemaKey,
                rootTypeParameterCount,
                uApiSchemaPseudoJson,
                schemaKeysToIndex,
                parsedTypes,
                typeExtensions,
                parseFailures,
                failedTypes,
            );
        } catch (e) {
            if (e instanceof UApiSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            }
        }
    }

    if (parseFailures.length > 0) {
        const offsetParseFailures = offsetSchemaIndex(parseFailures, pathOffset, schemaKeysToIndex, errorIndices);
        throw new UApiSchemaParseError(offsetParseFailures);
    }

    try {
        catchErrorCollisions(uApiSchemaPseudoJson, errorIndices, schemaKeysToIndex);

        for (const thisIndex of errorIndices) {
            const def_ = uApiSchemaPseudoJson[thisIndex] as { [key: string]: any };

            try {
                const error = parseErrorType(
                    def_,
                    uApiSchemaPseudoJson,
                    thisIndex,
                    schemaKeysToIndex,
                    parsedTypes,
                    typeExtensions,
                    parseFailures,
                    failedTypes,
                );
                applyErrorToParsedTypes(thisIndex, error, parsedTypes, schemaKeysToIndex);
            } catch (e) {
                if (e instanceof UApiSchemaParseError) {
                    parseFailures.push(...e.schemaParseFailures);
                }
            }
        }
    } catch (e) {
        if (e instanceof UApiSchemaParseError) {
            parseFailures.push(...e.schemaParseFailures);
        }
    }

    if (parseFailures.length > 0) {
        const offsetParseFailures = offsetSchemaIndex(parseFailures, pathOffset, schemaKeysToIndex, errorIndices);
        throw new UApiSchemaParseError(offsetParseFailures);
    }

    const requestHeaders: { [key: string]: UFieldDeclaration } = {};
    const responseHeaders: { [key: string]: UFieldDeclaration } = {};

    try {
        for (const requestHeaderKey of requestHeaderKeys) {
            const thisIndex = schemaKeysToIndex[requestHeaderKey];
            const def_ = uApiSchemaPseudoJson[thisIndex] as { [key: string]: any };
            const headerField = requestHeaderKey.slice('requestHeader.'.length);

            try {
                const requestHeaderType = parseHeadersType(
                    def_,
                    requestHeaderKey,
                    headerField,
                    thisIndex,
                    uApiSchemaPseudoJson,
                    schemaKeysToIndex,
                    parsedTypes,
                    typeExtensions,
                    parseFailures,
                    failedTypes,
                );
                requestHeaders[requestHeaderType.fieldName] = requestHeaderType;
            } catch (e) {
                if (e instanceof UApiSchemaParseError) {
                    parseFailures.push(...e.schemaParseFailures);
                }
            }
        }

        for (const responseHeaderKey of responseHeaderKeys) {
            const thisIndex = schemaKeysToIndex[responseHeaderKey];
            const def_ = uApiSchemaPseudoJson[thisIndex] as { [key: string]: any };
            const headerField = responseHeaderKey.slice('responseHeader.'.length);

            try {
                const responseHeaderType = parseHeadersType(
                    def_,
                    responseHeaderKey,
                    headerField,
                    thisIndex,
                    uApiSchemaPseudoJson,
                    schemaKeysToIndex,
                    parsedTypes,
                    typeExtensions,
                    parseFailures,
                    failedTypes,
                );
                responseHeaders[responseHeaderType.fieldName] = responseHeaderType;
            } catch (e) {
                if (e instanceof UApiSchemaParseError) {
                    parseFailures.push(...e.schemaParseFailures);
                }
            }
        }
    } catch (e) {
        if (e instanceof UApiSchemaParseError) {
            parseFailures.push(...e.schemaParseFailures);
        }
    }

    if (parseFailures.length > 0) {
        const offsetParseFailures = offsetSchemaIndex(parseFailures, pathOffset, schemaKeysToIndex, errorIndices);
        throw new UApiSchemaParseError(offsetParseFailures);
    }

    return new UApiSchema(uApiSchemaPseudoJson, parsedTypes, requestHeaders, responseHeaders, typeExtensions);
}
