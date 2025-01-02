import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { UFieldDeclaration } from '../../internal/types/UFieldDeclaration';
import { UType } from '../../internal/types/UType';
import { UApiSchemaParseError } from '../../UApiSchemaParseError';
import { getTypeUnexpectedParseFailure } from './GetTypeUnexpectedParseFailure';
import { parseTypeDeclaration } from './ParseTypeDeclaration';

export function parseField(
    documentName: string,
    path: any[],
    fieldDeclaration: string,
    typeDeclarationValue: any,
    uapiSchemaDocumentNamesToPseudoJson: { [key: string]: any[] },
    schemaKeysToDocumentName: { [key: string]: string },
    schemaKeysToIndex: { [key: string]: number },
    parsedTypes: { [key: string]: UType },
    allParseFailures: SchemaParseFailure[],
    failedTypes: Set<string>,
): UFieldDeclaration {
    const regexString = '^([a-z][a-zA-Z0-9_]*)(!)?$';
    const regex = new RegExp(regexString);

    const matcher = fieldDeclaration.match(regex);
    if (!matcher) {
        const finalPath = [...path, fieldDeclaration];
        throw new UApiSchemaParseError([
            new SchemaParseFailure(documentName, finalPath, 'KeyRegexMatchFailed', { regex: regexString }),
        ]);
    }

    const fieldName = matcher[0];
    const optional = Boolean(matcher[2]);

    const thisPath = [...path, fieldName];

    if (!Array.isArray(typeDeclarationValue)) {
        throw new UApiSchemaParseError(
            getTypeUnexpectedParseFailure(documentName, thisPath, typeDeclarationValue, 'Array'),
        );
    }
    const typeDeclarationArray = typeDeclarationValue;

    const typeDeclaration = parseTypeDeclaration(
        documentName,
        thisPath,
        typeDeclarationArray,
        uapiSchemaDocumentNamesToPseudoJson,
        schemaKeysToDocumentName,
        schemaKeysToIndex,
        parsedTypes,
        allParseFailures,
        failedTypes,
    );

    return new UFieldDeclaration(fieldName, typeDeclaration, optional);
}
