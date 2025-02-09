import { UApiSchemaParseError } from '../../UApiSchemaParseError';
import { getTypeUnexpectedParseFailure } from '../../internal/schema/GetTypeUnexpectedParseFailure';
import { UFieldDeclaration } from '../../internal/types/UFieldDeclaration';
import { ParseContext } from '../../internal/schema/ParseContext';
import { parseStructFields } from './ParseStructFields';
import { SchemaParseFailure } from './SchemaParseFailure';
import { UHeaders } from '../../internal/types/UHeaders';

export function parseHeadersType(
    path: any[],
    headersDefinitionAsParsedJson: { [key: string]: any },
    schemaKey: string,
    ctx: ParseContext,
): UHeaders {
    const parseFailures: SchemaParseFailure[] = [];
    const requestHeaders: { [key: string]: UFieldDeclaration } = {};
    const responseHeaders: { [key: string]: UFieldDeclaration } = {};

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
            const requestFields = parseStructFields(path, requestHeadersDef, ctx);

            // All headers are optional
            for (const field in requestFields) {
                requestFields[field].optional = true;
            }

            Object.assign(requestHeaders, requestFields);
        } catch (e) {
            if (e instanceof UApiSchemaParseError) {
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
            const responseFields = parseStructFields(path, responseHeadersDef, ctx);

            // All headers are optional
            for (const field in responseFields) {
                responseFields[field].optional = true;
            }

            Object.assign(responseHeaders, responseFields);
        } catch (e) {
            if (e instanceof UApiSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            } else {
                throw e;
            }
        }
    }

    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures, ctx.uapiSchemaDocumentNamesToJson);
    }

    return new UHeaders(schemaKey, requestHeaders, responseHeaders);
}
