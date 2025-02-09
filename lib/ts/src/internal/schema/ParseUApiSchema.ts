import { UApiSchema } from '../../UApiSchema';
import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { UType } from '../../internal/types/UType';
import { UFieldDeclaration } from '../../internal/types/UFieldDeclaration';
import { UApiSchemaParseError } from '../../UApiSchemaParseError';
import { applyErrorToParsedTypes } from '../../internal/schema/ApplyErrorToParsedTypes';
import { catchErrorCollisions } from '../../internal/schema/CatchErrorCollisions';
import { findMatchingSchemaKey } from '../../internal/schema/FindMatchingSchemaKey';
import { findSchemaKey } from '../../internal/schema/FindSchemaKey';
import { getOrParseType } from '../../internal/schema/GetOrParseType';
import { getTypeUnexpectedParseFailure } from '../../internal/schema/GetTypeUnexpectedParseFailure';
import { parseErrorType } from '../../internal/schema/ParseErrorType';
import { parseHeadersType } from '../../internal/schema/ParseHeadersType';
import { UError } from '../../internal/types/UError';
import { ParseContext } from '../../internal/schema/ParseContext';
import { getPathDocumentCoordinatesPseudoJson } from './GetPathDocumentCoordinatesPseudoJson';

export function parseUApiSchema(uApiSchemaDocumentNamesToJson: Record<string, string>): UApiSchema {
    const originalSchema: { [key: string]: Record<string, object> } = {};
    const fullSchema: { [key: string]: Record<string, object> } = {};
    const parsedTypes: { [key: string]: UType } = {};
    const parseFailures: SchemaParseFailure[] = [];
    const failedTypes: Set<string> = new Set();
    const schemaKeysToIndex: { [key: string]: number } = {};
    const schemaKeysToDocumentName: { [key: string]: string } = {};
    const schemaKeys: Set<string> = new Set();

    const orderedDocumentNames = Object.keys(uApiSchemaDocumentNamesToJson).sort();

    const uApiSchemaDocumentNamesToPseudoJson: Record<string, any[]> = {};

    for (const [documentName, jsonValue] of Object.entries(uApiSchemaDocumentNamesToJson)) {
        let uApiSchemaPseudoJsonInit: any;
        try {
            uApiSchemaPseudoJsonInit = JSON.parse(jsonValue);
        } catch (e) {
            throw new UApiSchemaParseError(
                [new SchemaParseFailure(documentName, [], 'JsonInvalid', {})],
                uApiSchemaDocumentNamesToJson,
                e as Error,
            );
        }

        if (!Array.isArray(uApiSchemaPseudoJsonInit)) {
            const thisParseFailure = getTypeUnexpectedParseFailure(documentName, [], uApiSchemaPseudoJsonInit, 'Array');
            throw new UApiSchemaParseError(thisParseFailure, uApiSchemaDocumentNamesToJson);
        }
        const uApiSchemaPseudoJson: any[] = uApiSchemaPseudoJsonInit;

        uApiSchemaDocumentNamesToPseudoJson[documentName] = uApiSchemaPseudoJson;
    }

    for (const documentName of orderedDocumentNames) {
        const uApiSchemaPseudoJson = uApiSchemaDocumentNamesToPseudoJson[documentName];

        let index = -1;
        for (const definition of uApiSchemaPseudoJson) {
            index += 1;
            const loopPath = [index];

            if (
                typeof definition !== 'object' ||
                Array.isArray(definition) ||
                definition === null ||
                definition === undefined
            ) {
                const thisParseFailures = getTypeUnexpectedParseFailure(
                    documentName,
                    loopPath as any[],
                    definition,
                    'Object',
                );
                parseFailures.push(...thisParseFailures);
                continue;
            }

            const def_: Record<string, object> = definition as Record<string, object>;

            try {
                const schemaKey = findSchemaKey(documentName, def_, index, uApiSchemaDocumentNamesToJson);
                const matchingSchemaKey = findMatchingSchemaKey(schemaKeys, schemaKey);
                if (matchingSchemaKey !== null) {
                    const otherPathIndex = schemaKeysToIndex[matchingSchemaKey];
                    const otherDocumentName = schemaKeysToDocumentName[matchingSchemaKey];
                    const finalPath = [...loopPath, schemaKey];
                    const otherFinalPath = [otherPathIndex, matchingSchemaKey];
                    const otherDocumentJson = uApiSchemaDocumentNamesToJson[otherDocumentName];
                    const otherLocationPseudoJson = getPathDocumentCoordinatesPseudoJson(
                        otherFinalPath,
                        otherDocumentJson,
                    );
                    parseFailures.push(
                        new SchemaParseFailure(documentName, finalPath as any[], 'PathCollision', {
                            document: otherDocumentName,
                            location: otherLocationPseudoJson,
                            path: [otherPathIndex, matchingSchemaKey],
                        }),
                    );
                    continue;
                }

                schemaKeys.add(schemaKey);
                schemaKeysToIndex[schemaKey] = index;
                schemaKeysToDocumentName[schemaKey] = documentName;
                if ('auto_' === documentName || !documentName.endsWith('_')) {
                    originalSchema[schemaKey] = def_;
                }
                fullSchema[schemaKey] = def_;
            } catch (e) {
                if (e instanceof UApiSchemaParseError) {
                    parseFailures.push(...e.schemaParseFailures);
                } else {
                    throw e;
                }
            }
        }
    }

    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures, uApiSchemaDocumentNamesToJson);
    }

    const headerKeys: Set<string> = new Set();
    const responseHeaderKeys: Set<string> = new Set();
    const errorKeys: Set<string> = new Set();

    for (const schemaKey of schemaKeys) {
        if (schemaKey.startsWith('info.')) {
            continue;
        } else if (schemaKey.startsWith('headers.')) {
            headerKeys.add(schemaKey);
            continue;
        } else if (schemaKey.startsWith('errors.')) {
            errorKeys.add(schemaKey);
            continue;
        }

        const thisIndex = schemaKeysToIndex[schemaKey];
        const thisDocumentName = schemaKeysToDocumentName[schemaKey];

        try {
            getOrParseType(
                [thisIndex],
                schemaKey,
                new ParseContext(
                    thisDocumentName,
                    uApiSchemaDocumentNamesToPseudoJson,
                    uApiSchemaDocumentNamesToJson,
                    schemaKeysToDocumentName,
                    schemaKeysToIndex,
                    parsedTypes,
                    parseFailures,
                    failedTypes,
                ),
            );
        } catch (e) {
            if (e instanceof UApiSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            } else {
                throw e;
            }
        }
    }

    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures, uApiSchemaDocumentNamesToJson);
    }

    const errors: UError[] = [];

    try {
        for (const thisKey of errorKeys) {
            const thisIndex = schemaKeysToIndex[thisKey];
            const thisDocumentName = schemaKeysToDocumentName[thisKey];
            const uApiSchemaPseudoJson = uApiSchemaDocumentNamesToPseudoJson[thisDocumentName];
            const def_ = uApiSchemaPseudoJson[thisIndex] as { [key: string]: any };

            try {
                const error = parseErrorType(
                    [thisIndex],
                    def_,
                    thisKey,
                    new ParseContext(
                        thisDocumentName,
                        uApiSchemaDocumentNamesToPseudoJson,
                        uApiSchemaDocumentNamesToJson,
                        schemaKeysToDocumentName,
                        schemaKeysToIndex,
                        parsedTypes,
                        parseFailures,
                        failedTypes,
                    ),
                );
                errors.push(error);
            } catch (e) {
                if (e instanceof UApiSchemaParseError) {
                    parseFailures.push(...e.schemaParseFailures);
                } else {
                    throw e;
                }
            }
        }
    } catch (e) {
        if (e instanceof UApiSchemaParseError) {
            parseFailures.push(...e.schemaParseFailures);
        } else {
            throw e;
        }
    }

    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures, uApiSchemaDocumentNamesToJson);
    }

    try {
        catchErrorCollisions(
            uApiSchemaDocumentNamesToPseudoJson,
            errorKeys,
            schemaKeysToIndex,
            schemaKeysToDocumentName,
            uApiSchemaDocumentNamesToJson,
        );
    } catch (e) {
        if (e instanceof UApiSchemaParseError) {
            parseFailures.push(...e.schemaParseFailures);
        } else {
            throw e;
        }
    }

    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures, uApiSchemaDocumentNamesToJson);
    }

    for (const error of errors) {
        try {
            applyErrorToParsedTypes(
                error,
                parsedTypes,
                schemaKeysToDocumentName,
                schemaKeysToIndex,
                uApiSchemaDocumentNamesToJson,
            );
        } catch (e) {
            if (e instanceof UApiSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            } else {
                throw e;
            }
        }
    }

    const requestHeaders: { [key: string]: UFieldDeclaration } = {};
    const responseHeaders: { [key: string]: UFieldDeclaration } = {};

    for (const headerKey of headerKeys) {
        const thisIndex = schemaKeysToIndex[headerKey];
        const thisDocumentName = schemaKeysToDocumentName[headerKey];
        const uApiSchemaPseudoJson = uApiSchemaDocumentNamesToPseudoJson[thisDocumentName];
        const def_ = uApiSchemaPseudoJson[thisIndex] as { [key: string]: any };

        try {
            const requestHeaderType = parseHeadersType(
                [thisIndex],
                def_,
                headerKey,
                new ParseContext(
                    thisDocumentName,
                    uApiSchemaDocumentNamesToPseudoJson,
                    uApiSchemaDocumentNamesToJson,
                    schemaKeysToDocumentName,
                    schemaKeysToIndex,
                    parsedTypes,
                    parseFailures,
                    failedTypes,
                ),
            );
            Object.assign(requestHeaders, requestHeaderType.requestHeaders);
            Object.assign(responseHeaders, requestHeaderType.responseHeaders);
        } catch (e) {
            if (e instanceof UApiSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            } else {
                throw e;
            }
        }
    }

    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures, uApiSchemaDocumentNamesToJson);
    }

    const sortKeys = (a: string, b: string) => {
        const aStartsWithInfo = a.startsWith('info.');
        const bStartsWithInfo = b.startsWith('info.');
        if (aStartsWithInfo && !bStartsWithInfo) return -1;
        if (!aStartsWithInfo && bStartsWithInfo) return 1;
        return a < b ? -1 : a > b ? 1 : 0;
    };

    const sortedSchemaKeys = Object.keys(originalSchema).sort(sortKeys);
    const finalOriginalSchema: Record<string, object>[] = sortedSchemaKeys.map((key) => originalSchema[key]);

    const sortedFullSchemaKeys = Object.keys(fullSchema).sort(sortKeys);
    const finalFullSchema: Record<string, object>[] = sortedFullSchemaKeys.map((key) => fullSchema[key]);

    return new UApiSchema(finalOriginalSchema, finalFullSchema, parsedTypes, requestHeaders, responseHeaders);
}
