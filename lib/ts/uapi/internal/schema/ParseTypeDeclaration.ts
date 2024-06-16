import * as re from 're';
import { TYPE_CHECKING } from 'typing';
import { SchemaParseFailure } from 'uapi/internal/schema/SchemaParseFailure';
import { UTypeDeclaration } from 'uapi/internal/types/UTypeDeclaration';
import { UType } from 'uapi/internal/types/UType';
import { UApiSchemaParseError } from 'uapi/UApiSchemaParseError';
import { getOrParseType } from 'uapi/internal/schema/GetOrParseType';
import { getTypeUnexpectedParseFailure } from 'uapi/internal/schema/GetTypeUnexpectedParseFailure';
import { UGeneric } from 'uapi/internal/types/UGeneric';

if (TYPE_CHECKING) {
}

export function parseTypeDeclaration(
    path: any[],
    typeDeclarationArray: any[],
    thisTypeParameterCount: number,
    uapiSchemaPseudoJson: any[],
    schemaKeysToIndex: { [key: string]: number },
    parsedTypes: { [key: string]: any },
    typeExtensions: { [key: string]: any },
    allParseFailures: SchemaParseFailure[],
    failedTypes: Set<string>,
): UTypeDeclaration {
    if (!typeDeclarationArray.length) {
        throw new UApiSchemaParseError([new SchemaParseFailure(path, 'EmptyArrayDisallowed', {}, null)]);
    }

    const basePath = path.concat([0]);
    const baseType = typeDeclarationArray[0];

    if (typeof baseType !== 'string') {
        const thisParseFailures = getTypeUnexpectedParseFailure(basePath, baseType, 'String');
        throw new UApiSchemaParseError(thisParseFailures);
    }

    const rootTypeString = baseType;

    const regexString = '^(.+?)(\\?)?$';
    const regex = new re.Regex(regexString);

    const matcher = regex.match(rootTypeString);
    if (!matcher) {
        throw new UApiSchemaParseError([
            new SchemaParseFailure(basePath, 'StringRegexMatchFailed', { regex: regexString }, null),
        ]);
    }

    const typeName = matcher.group(1);
    const nullable = !!matcher.group(2);

    const type_ = getOrParseType(
        basePath,
        typeName,
        thisTypeParameterCount,
        uapiSchemaPseudoJson,
        schemaKeysToIndex,
        parsedTypes,
        typeExtensions,
        allParseFailures,
        failedTypes,
    );

    if (type_ instanceof UGeneric && nullable) {
        throw new UApiSchemaParseError([
            new SchemaParseFailure(basePath, 'StringRegexMatchFailed', { regex: '^(.+?)[^?]$' }, null),
        ]);
    }

    const givenTypeParameterCount = typeDeclarationArray.length - 1;
    if (type_.getTypeParameterCount() !== givenTypeParameterCount) {
        throw new UApiSchemaParseError([
            new SchemaParseFailure(
                path,
                'ArrayLengthUnexpected',
                { actual: typeDeclarationArray.length, expected: type_.getTypeParameterCount() + 1 },
                null,
            ),
        ]);
    }

    const parseFailures: SchemaParseFailure[] = [];
    const typeParameters: UTypeDeclaration[] = [];
    const givenTypeParameters = typeDeclarationArray.slice(1);

    for (let index = 1; index <= givenTypeParameters.length; index++) {
        const e = givenTypeParameters[index - 1];
        const loopPath = path.concat([index]);

        if (!Array.isArray(e)) {
            const thisParseFailures = getTypeUnexpectedParseFailure(loopPath, e, 'Array');
            parseFailures.push(...thisParseFailures);
            continue;
        }

        const l = e;

        try {
            const typeParameterTypeDeclaration = parseTypeDeclaration(
                loopPath,
                l,
                thisTypeParameterCount,
                uapiSchemaPseudoJson,
                schemaKeysToIndex,
                parsedTypes,
                typeExtensions,
                allParseFailures,
                failedTypes,
            );

            typeParameters.push(typeParameterTypeDeclaration);
        } catch (e2) {
            parseFailures.push(...e2.schemaParseFailures);
        }
    }

    if (parseFailures.length) {
        throw new UApiSchemaParseError(parseFailures);
    }

    return new UTypeDeclaration(type_, nullable, typeParameters);
}
