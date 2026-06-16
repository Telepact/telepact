//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { TelepactSchemaParseError } from '../../TelepactSchemaParseError.js';
import { getTypeUnexpectedParseFailure } from '../../internal/schema/GetTypeUnexpectedParseFailure.js';
import { TFieldDeclaration } from '../types/TFieldDeclaration.js';
import { ParseContext } from '../../internal/schema/ParseContext.js';
import { parseStructFields } from './ParseStructFields.js';
import { SchemaParseFailure } from './SchemaParseFailure.js';
import { THeaders } from '../types/THeaders.js';

export function parseHeadersType(
    path: any[],
    headersDefinitionAsParsedJson: { [key: string]: any },
    schemaKey: string,
    ctx: ParseContext,
): THeaders {
    const parseFailures: SchemaParseFailure[] = [];
    const requestHeaders: { [key: string]: TFieldDeclaration } = {};
    const responseHeaders: { [key: string]: TFieldDeclaration } = {};

    const requestHeadersDef = headersDefinitionAsParsedJson[schemaKey];

    const thisPath = [...path, schemaKey];

    if (
        typeof requestHeadersDef !== 'object' ||
        Array.isArray(requestHeadersDef) ||
        requestHeadersDef === null ||
        requestHeadersDef === undefined
    ) {
        const branchParseFailures = getTypeUnexpectedParseFailure(
            ctx.documentName,
            thisPath,
            requestHeadersDef,
            'Object',
        );
        parseFailures.push(...branchParseFailures);
    } else {
        try {
            const isHeader = true;
            const requestFields = parseStructFields(thisPath, requestHeadersDef, isHeader, ctx);

            // All headers are optional
            for (const field in requestFields) {
                requestFields[field].optional = true;
            }

            Object.assign(requestHeaders, requestFields);
        } catch (e) {
            if (e instanceof TelepactSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            } else {
                throw e;
            }
        }
    }

    const responseKey = '->';
    const responsePath = [...path, responseKey];

    if (!(responseKey in headersDefinitionAsParsedJson)) {
        parseFailures.push(
            new SchemaParseFailure(ctx.documentName, responsePath, 'RequiredObjectKeyMissing', {
                key: responseKey,
            }),
        );
    }

    const responseHeadersDef = headersDefinitionAsParsedJson[responseKey];

    if (
        typeof responseHeadersDef !== 'object' ||
        Array.isArray(responseHeadersDef) ||
        responseHeadersDef === null ||
        responseHeadersDef === undefined
    ) {
        const branchParseFailures = getTypeUnexpectedParseFailure(
            ctx.documentName,
            thisPath,
            responseHeadersDef,
            'Object',
        );
        parseFailures.push(...branchParseFailures);
    } else {
        try {
            const isHeader = true;
            const responseFields = parseStructFields(responsePath, responseHeadersDef, isHeader, ctx);

            // All headers are optional
            for (const field in responseFields) {
                responseFields[field].optional = true;
            }

            Object.assign(responseHeaders, responseFields);
        } catch (e) {
            if (e instanceof TelepactSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            } else {
                throw e;
            }
        }
    }

    if (parseFailures.length > 0) {
        throw new TelepactSchemaParseError(parseFailures, ctx.telepactSchemaDocumentNamesToJson);
    }

    return new THeaders(schemaKey, requestHeaders, responseHeaders);
}
