import { MsgPactSchema } from '../../MsgPactSchema';
import { SchemaParseFailure } from './SchemaParseFailure';
import { VType } from '../types/VType';
import { VFieldDeclaration } from '../types/VFieldDeclaration';
import { MsgPactSchemaParseError } from '../../MsgPactSchemaParseError';
import { applyErrorToParsedTypes } from './ApplyErrorToParsedTypes';
import { catchErrorCollisions } from './CatchErrorCollisions';
import { findMatchingSchemaKey } from './FindMatchingSchemaKey';
import { findSchemaKey } from './FindSchemaKey';
import { getOrParseType } from './GetOrParseType';
import { getTypeUnexpectedParseFailure } from './GetTypeUnexpectedParseFailure';
import { parseErrorType } from './ParseErrorType';
import { parseHeadersType } from './ParseHeadersType';
import { VError } from '../types/VError';
import { ParseContext } from './ParseContext';
import { getPathDocumentCoordinatesPseudoJson } from './GetPathDocumentCoordinatesPseudoJson';
import { VHeaders } from '../types/VHeaders';
import { catchHeaderCollisions } from './CatchHeaderCollisions';

export function parseMsgPactSchema(msgPactSchemaDocumentNamesToJson: Record<string, string>): MsgPactSchema {
    const originalSchema: { [key: string]: Record<string, object> } = {};
    const fullSchema: { [key: string]: Record<string, object> } = {};
    const parsedTypes: { [key: string]: VType } = {};
    const parseFailures: SchemaParseFailure[] = [];
    const failedTypes: Set<string> = new Set();
    const schemaKeysToIndex: { [key: string]: number } = {};
    const schemaKeysToDocumentName: { [key: string]: string } = {};
    const schemaKeys: Set<string> = new Set();

    const orderedDocumentNames = Object.keys(msgPactSchemaDocumentNamesToJson).sort();

    const msgPactSchemaDocumentNamesToPseudoJson: Record<string, any[]> = {};

    for (const [documentName, jsonValue] of Object.entries(msgPactSchemaDocumentNamesToJson)) {
        let msgPactSchemaPseudoJsonInit: any;
        try {
            msgPactSchemaPseudoJsonInit = JSON.parse(jsonValue);
        } catch (e) {
            throw new MsgPactSchemaParseError(
                [new SchemaParseFailure(documentName, [], 'JsonInvalid', {})],
                msgPactSchemaDocumentNamesToJson,
                e as Error,
            );
        }

        if (!Array.isArray(msgPactSchemaPseudoJsonInit)) {
            const thisParseFailure = getTypeUnexpectedParseFailure(documentName, [], msgPactSchemaPseudoJsonInit, 'Array');
            throw new MsgPactSchemaParseError(thisParseFailure, msgPactSchemaDocumentNamesToJson);
        }
        const msgPactSchemaPseudoJson: any[] = msgPactSchemaPseudoJsonInit;

        msgPactSchemaDocumentNamesToPseudoJson[documentName] = msgPactSchemaPseudoJson;
    }

    for (const documentName of orderedDocumentNames) {
        const msgPactSchemaPseudoJson = msgPactSchemaDocumentNamesToPseudoJson[documentName];

        let index = -1;
        for (const definition of msgPactSchemaPseudoJson) {
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
                const schemaKey = findSchemaKey(documentName, def_, index, msgPactSchemaDocumentNamesToJson);
                const matchingSchemaKey = findMatchingSchemaKey(schemaKeys, schemaKey);
                if (matchingSchemaKey !== null) {
                    const otherPathIndex = schemaKeysToIndex[matchingSchemaKey];
                    const otherDocumentName = schemaKeysToDocumentName[matchingSchemaKey];
                    const finalPath = [...loopPath, schemaKey];
                    const otherFinalPath = [otherPathIndex, matchingSchemaKey];
                    const otherDocumentJson = msgPactSchemaDocumentNamesToJson[otherDocumentName];
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
                if (e instanceof MsgPactSchemaParseError) {
                    parseFailures.push(...e.schemaParseFailures);
                } else {
                    throw e;
                }
            }
        }
    }

    if (parseFailures.length > 0) {
        throw new MsgPactSchemaParseError(parseFailures, msgPactSchemaDocumentNamesToJson);
    }

    const headerKeys: Set<string> = new Set();
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
                    msgPactSchemaDocumentNamesToPseudoJson,
                    msgPactSchemaDocumentNamesToJson,
                    schemaKeysToDocumentName,
                    schemaKeysToIndex,
                    parsedTypes,
                    parseFailures,
                    failedTypes,
                ),
            );
        } catch (e) {
            if (e instanceof MsgPactSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            } else {
                throw e;
            }
        }
    }

    if (parseFailures.length > 0) {
        throw new MsgPactSchemaParseError(parseFailures, msgPactSchemaDocumentNamesToJson);
    }

    const errors: VError[] = [];

    try {
        for (const thisKey of errorKeys) {
            const thisIndex = schemaKeysToIndex[thisKey];
            const thisDocumentName = schemaKeysToDocumentName[thisKey];
            const msgPactSchemaPseudoJson = msgPactSchemaDocumentNamesToPseudoJson[thisDocumentName];
            const def_ = msgPactSchemaPseudoJson[thisIndex] as { [key: string]: any };

            try {
                const error = parseErrorType(
                    [thisIndex],
                    def_,
                    thisKey,
                    new ParseContext(
                        thisDocumentName,
                        msgPactSchemaDocumentNamesToPseudoJson,
                        msgPactSchemaDocumentNamesToJson,
                        schemaKeysToDocumentName,
                        schemaKeysToIndex,
                        parsedTypes,
                        parseFailures,
                        failedTypes,
                    ),
                );
                errors.push(error);
            } catch (e) {
                if (e instanceof MsgPactSchemaParseError) {
                    parseFailures.push(...e.schemaParseFailures);
                } else {
                    throw e;
                }
            }
        }
    } catch (e) {
        if (e instanceof MsgPactSchemaParseError) {
            parseFailures.push(...e.schemaParseFailures);
        } else {
            throw e;
        }
    }

    if (parseFailures.length > 0) {
        throw new MsgPactSchemaParseError(parseFailures, msgPactSchemaDocumentNamesToJson);
    }

    try {
        catchErrorCollisions(
            msgPactSchemaDocumentNamesToPseudoJson,
            errorKeys,
            schemaKeysToIndex,
            schemaKeysToDocumentName,
            msgPactSchemaDocumentNamesToJson,
        );
    } catch (e) {
        if (e instanceof MsgPactSchemaParseError) {
            parseFailures.push(...e.schemaParseFailures);
        } else {
            throw e;
        }
    }

    if (parseFailures.length > 0) {
        throw new MsgPactSchemaParseError(parseFailures, msgPactSchemaDocumentNamesToJson);
    }

    for (const error of errors) {
        try {
            applyErrorToParsedTypes(
                error,
                parsedTypes,
                schemaKeysToDocumentName,
                schemaKeysToIndex,
                msgPactSchemaDocumentNamesToJson,
            );
        } catch (e) {
            if (e instanceof MsgPactSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            } else {
                throw e;
            }
        }
    }

    const headers: VHeaders[] = [];

    for (const headerKey of headerKeys) {
        const thisIndex = schemaKeysToIndex[headerKey];
        const thisDocumentName = schemaKeysToDocumentName[headerKey];
        const msgPactSchemaPseudoJson = msgPactSchemaDocumentNamesToPseudoJson[thisDocumentName];
        const def_ = msgPactSchemaPseudoJson[thisIndex] as { [key: string]: any };

        try {
            const headerType = parseHeadersType(
                [thisIndex],
                def_,
                headerKey,
                new ParseContext(
                    thisDocumentName,
                    msgPactSchemaDocumentNamesToPseudoJson,
                    msgPactSchemaDocumentNamesToJson,
                    schemaKeysToDocumentName,
                    schemaKeysToIndex,
                    parsedTypes,
                    parseFailures,
                    failedTypes,
                ),
            );
            headers.push(headerType);
        } catch (e) {
            if (e instanceof MsgPactSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            } else {
                throw e;
            }
        }
    }

    if (parseFailures.length > 0) {
        throw new MsgPactSchemaParseError(parseFailures, msgPactSchemaDocumentNamesToJson);
    }

    try {
        catchHeaderCollisions(
            msgPactSchemaDocumentNamesToPseudoJson,
            headerKeys,
            schemaKeysToIndex,
            schemaKeysToDocumentName,
            msgPactSchemaDocumentNamesToJson,
        );
    } catch (e) {
        if (e instanceof MsgPactSchemaParseError) {
            parseFailures.push(...e.schemaParseFailures);
        } else {
            throw e;
        }
    }

    if (parseFailures.length > 0) {
        throw new MsgPactSchemaParseError(parseFailures, msgPactSchemaDocumentNamesToJson);
    }

    const requestHeaders: { [key: string]: VFieldDeclaration } = {};
    const responseHeaders: { [key: string]: VFieldDeclaration } = {};

    for (const header of headers) {
        Object.assign(requestHeaders, header.requestHeaders);
        Object.assign(responseHeaders, header.responseHeaders);
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

    return new MsgPactSchema(finalOriginalSchema, finalFullSchema, parsedTypes, requestHeaders, responseHeaders);
}
