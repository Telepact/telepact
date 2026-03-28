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

import { TelepactSchemaParseError } from '../../TelepactSchemaParseError';
import { getTypeUnexpectedParseFailure } from '../../internal/schema/GetTypeUnexpectedParseFailure';
import { TFieldDeclaration } from '../types/TFieldDeclaration';
import { ParseContext } from '../../internal/schema/ParseContext';
import { parseStructFields } from './ParseStructFields';
import { SchemaParseFailure } from './SchemaParseFailure';
import { THeaders } from '../types/THeaders';

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
