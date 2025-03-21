import { TelepactSchemaParseError } from '../../TelepactSchemaParseError';
import { getTypeUnexpectedParseFailure } from '../../internal/schema/GetTypeUnexpectedParseFailure';
import { VFieldDeclaration } from '../types/VFieldDeclaration';
import { ParseContext } from '../../internal/schema/ParseContext';
import { parseStructFields } from './ParseStructFields';
import { SchemaParseFailure } from './SchemaParseFailure';
import { VHeaders } from '../types/VHeaders';

export function parseHeadersType(
    path: any[],
    headersDefinitionAsParsedJson: { [key: string]: any },
    schemaKey: string,
    ctx: ParseContext,
): VHeaders {
    const parseFailures: SchemaParseFailure[] = [];
    const requestHeaders: { [key: string]: VFieldDeclaration } = {};
    const responseHeaders: { [key: string]: VFieldDeclaration } = {};

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
            const requestFields = parseStructFields(thisPath, requestHeadersDef, ctx);

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
            const responseFields = parseStructFields(responsePath, responseHeadersDef, ctx);

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

    return new VHeaders(schemaKey, requestHeaders, responseHeaders);
}
