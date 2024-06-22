import { SchemaParseFailure } from 'uapi/internal/schema/SchemaParseFailure';
import { UFieldDeclaration } from 'uapi/internal/types/UFieldDeclaration';
import { UType } from 'uapi/internal/types/UType';
import { UApiSchemaParseError } from 'uapi/UApiSchemaParseError';
import { getTypeUnexpectedParseFailure } from './GetTypeUnexpectedParseFailure';
import { parseTypeDeclaration } from './ParseTypeDeclaration';

export function parseField(
    path: any[],
    fieldDeclaration: string,
    typeDeclarationValue: any,
    typeParameterCount: number,
    uapiSchemaPseudoJson: any[],
    schemaKeysToIndex: { [key: string]: number },
    parsedTypes: { [key: string]: UType },
    typeExtensions: { [key: string]: UType },
    allParseFailures: SchemaParseFailure[],
    failedTypes: Set<string>,
): UFieldDeclaration {
    const regexString = '^([a-z][a-zA-Z0-9_]*)(!)?$';
    const regex = new RegExp(regexString);

    const matcher = fieldDeclaration.match(regex);
    if (!matcher) {
        const finalPath = [...path, fieldDeclaration];
        throw new UApiSchemaParseError([
            new SchemaParseFailure(finalPath, 'KeyRegexMatchFailed', { regex: regexString }, null),
        ]);
    }

    const fieldName = matcher[0];
    const optional = Boolean(matcher[2]);

    const thisPath = [...path, fieldName];

    if (!Array.isArray(typeDeclarationValue)) {
        throw new UApiSchemaParseError(getTypeUnexpectedParseFailure(thisPath, typeDeclarationValue, 'Array'));
    }
    const typeDeclarationArray = typeDeclarationValue;

    const typeDeclaration = parseTypeDeclaration(
        thisPath,
        typeDeclarationArray,
        typeParameterCount,
        uapiSchemaPseudoJson,
        schemaKeysToIndex,
        parsedTypes,
        typeExtensions,
        allParseFailures,
        failedTypes,
    );

    return new UFieldDeclaration(fieldName, typeDeclaration, optional);
}
