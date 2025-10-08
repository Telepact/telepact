//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

import { TelepactSchema } from '../../TelepactSchema';
import { SchemaParseFailure } from './SchemaParseFailure';
import { TType } from '../types/TType';
import { TFieldDeclaration } from '../types/TFieldDeclaration';
import { TelepactSchemaParseError } from '../../TelepactSchemaParseError';
import { applyErrorToParsedTypes } from './ApplyErrorToParsedTypes';
import { catchErrorCollisions } from './CatchErrorCollisions';
import { findMatchingSchemaKey } from './FindMatchingSchemaKey';
import { findSchemaKey } from './FindSchemaKey';
import { getOrParseType } from './GetOrParseType';
import { getTypeUnexpectedParseFailure } from './GetTypeUnexpectedParseFailure';
import { parseErrorType } from './ParseErrorType';
import { parseHeadersType } from './ParseHeadersType';
import { TError } from '../types/TError';
import { ParseContext } from './ParseContext';
import { getPathDocumentCoordinatesPseudoJson } from './GetPathDocumentCoordinatesPseudoJson';
import { THeaders } from '../types/THeaders';
import { catchHeaderCollisions } from './CatchHeaderCollisions';

export function parseTelepactSchema(telepactSchemaDocumentNamesToJson: Record<string, string>): TelepactSchema {
    const originalSchema: { [key: string]: Record<string, object> } = {};
    const fullSchema: { [key: string]: Record<string, object> } = {};
    const parsedTypes: { [key: string]: TType } = {};
    const parseFailures: SchemaParseFailure[] = [];
    const fnErrorRegexes: { [key: string]: string } = {};
    const failedTypes: Set<string> = new Set();
    const schemaKeysToIndex: { [key: string]: number } = {};
    const schemaKeysToDocumentName: { [key: string]: string } = {};
    const schemaKeys: Set<string> = new Set();

    const orderedDocumentNames = Object.keys(telepactSchemaDocumentNamesToJson).sort();

    const telepactSchemaDocumentNamesToPseudoJson: Record<string, any[]> = {};

    for (const [documentName, jsonValue] of Object.entries(telepactSchemaDocumentNamesToJson)) {
        let telepactSchemaPseudoJsonInit: any;
        try {
            telepactSchemaPseudoJsonInit = JSON.parse(jsonValue);
        } catch (e) {
            throw new TelepactSchemaParseError(
                [new SchemaParseFailure(documentName, [], 'JsonInvalid', {})],
                telepactSchemaDocumentNamesToJson,
                e as Error,
            );
        }

        if (!Array.isArray(telepactSchemaPseudoJsonInit)) {
            const thisParseFailure = getTypeUnexpectedParseFailure(documentName, [], telepactSchemaPseudoJsonInit, 'Array');
            throw new TelepactSchemaParseError(thisParseFailure, telepactSchemaDocumentNamesToJson);
        }
        const telepactSchemaPseudoJson: any[] = telepactSchemaPseudoJsonInit;

        telepactSchemaDocumentNamesToPseudoJson[documentName] = telepactSchemaPseudoJson;
    }

    for (const documentName of orderedDocumentNames) {
        const telepactSchemaPseudoJson = telepactSchemaDocumentNamesToPseudoJson[documentName];

        let index = -1;
        for (const definition of telepactSchemaPseudoJson) {
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
                const schemaKey = findSchemaKey(documentName, def_, index, telepactSchemaDocumentNamesToJson);
                const matchingSchemaKey = findMatchingSchemaKey(schemaKeys, schemaKey);
                if (matchingSchemaKey !== null) {
                    const otherPathIndex = schemaKeysToIndex[matchingSchemaKey];
                    const otherDocumentName = schemaKeysToDocumentName[matchingSchemaKey];
                    const finalPath = [...loopPath, schemaKey];
                    const otherFinalPath = [otherPathIndex, matchingSchemaKey];
                    const otherDocumentJson = telepactSchemaDocumentNamesToJson[otherDocumentName];
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

                if ('auto_' === documentName || 'auth_' === documentName || !documentName.endsWith('_')) {
                    originalSchema[schemaKey] = def_;
                }
                fullSchema[schemaKey] = def_;
            } catch (e) {
                if (e instanceof TelepactSchemaParseError) {
                    parseFailures.push(...e.schemaParseFailures);
                } else {
                    throw e;
                }
            }
        }
    }

    if (parseFailures.length > 0) {
        throw new TelepactSchemaParseError(parseFailures, telepactSchemaDocumentNamesToJson);
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
                    telepactSchemaDocumentNamesToPseudoJson,
                    telepactSchemaDocumentNamesToJson,
                    schemaKeysToDocumentName,
                    schemaKeysToIndex,
                    parsedTypes,
                    fnErrorRegexes,
                    parseFailures,
                    failedTypes
                ),
            );
        } catch (e) {
            if (e instanceof TelepactSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            } else {
                throw e;
            }
        }
    }

    if (parseFailures.length > 0) {
        throw new TelepactSchemaParseError(parseFailures, telepactSchemaDocumentNamesToJson);
    }

    const errors: TError[] = [];

    try {
        for (const thisKey of errorKeys) {
            const thisIndex = schemaKeysToIndex[thisKey];
            const thisDocumentName = schemaKeysToDocumentName[thisKey];
            const telepactSchemaPseudoJson = telepactSchemaDocumentNamesToPseudoJson[thisDocumentName];
            const def_ = telepactSchemaPseudoJson[thisIndex] as { [key: string]: any };

            try {
                const error = parseErrorType(
                    [thisIndex],
                    def_,
                    thisKey,
                    new ParseContext(
                        thisDocumentName,
                        telepactSchemaDocumentNamesToPseudoJson,
                        telepactSchemaDocumentNamesToJson,
                        schemaKeysToDocumentName,
                        schemaKeysToIndex,
                        parsedTypes,
                        fnErrorRegexes,
                        parseFailures,
                        failedTypes
                    ),
                );
                errors.push(error);
            } catch (e) {
                if (e instanceof TelepactSchemaParseError) {
                    parseFailures.push(...e.schemaParseFailures);
                } else {
                    throw e;
                }
            }
        }
    } catch (e) {
        if (e instanceof TelepactSchemaParseError) {
            parseFailures.push(...e.schemaParseFailures);
        } else {
            throw e;
        }
    }

    if (parseFailures.length > 0) {
        throw new TelepactSchemaParseError(parseFailures, telepactSchemaDocumentNamesToJson);
    }

    try {
        catchErrorCollisions(
            telepactSchemaDocumentNamesToPseudoJson,
            errorKeys,
            schemaKeysToIndex,
            schemaKeysToDocumentName,
            telepactSchemaDocumentNamesToJson,
        );
    } catch (e) {
        if (e instanceof TelepactSchemaParseError) {
            parseFailures.push(...e.schemaParseFailures);
        } else {
            throw e;
        }
    }

    if (parseFailures.length > 0) {
        throw new TelepactSchemaParseError(parseFailures, telepactSchemaDocumentNamesToJson);
    }

    for (const error of errors) {
        try {
            applyErrorToParsedTypes(
                error,
                parsedTypes,
                schemaKeysToDocumentName,
                schemaKeysToIndex,
                telepactSchemaDocumentNamesToJson,
                fnErrorRegexes
            );
        } catch (e) {
            if (e instanceof TelepactSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            } else {
                throw e;
            }
        }
    }

    const headers: THeaders[] = [];

    for (const headerKey of headerKeys) {
        const thisIndex = schemaKeysToIndex[headerKey];
        const thisDocumentName = schemaKeysToDocumentName[headerKey];
        const telepactSchemaPseudoJson = telepactSchemaDocumentNamesToPseudoJson[thisDocumentName];
        const def_ = telepactSchemaPseudoJson[thisIndex] as { [key: string]: any };

        try {
            const headerType = parseHeadersType(
                [thisIndex],
                def_,
                headerKey,
                new ParseContext(
                    thisDocumentName,
                    telepactSchemaDocumentNamesToPseudoJson,
                    telepactSchemaDocumentNamesToJson,
                    schemaKeysToDocumentName,
                    schemaKeysToIndex,
                    parsedTypes,
                    fnErrorRegexes,
                    parseFailures,
                    failedTypes
                ),
            );
            headers.push(headerType);
        } catch (e) {
            if (e instanceof TelepactSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            } else {
                throw e;
            }
        }
    }

    if (parseFailures.length > 0) {
        throw new TelepactSchemaParseError(parseFailures, telepactSchemaDocumentNamesToJson);
    }

    try {
        catchHeaderCollisions(
            telepactSchemaDocumentNamesToPseudoJson,
            headerKeys,
            schemaKeysToIndex,
            schemaKeysToDocumentName,
            telepactSchemaDocumentNamesToJson,
        );
    } catch (e) {
        if (e instanceof TelepactSchemaParseError) {
            parseFailures.push(...e.schemaParseFailures);
        } else {
            throw e;
        }
    }

    if (parseFailures.length > 0) {
        throw new TelepactSchemaParseError(parseFailures, telepactSchemaDocumentNamesToJson);
    }

    const requestHeaders: { [key: string]: TFieldDeclaration } = {};
    const responseHeaders: { [key: string]: TFieldDeclaration } = {};

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

    return new TelepactSchema(finalOriginalSchema, finalFullSchema, parsedTypes, requestHeaders, responseHeaders);
}
