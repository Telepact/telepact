import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { UApiSchemaParseError } from '../../UApiSchemaParseError';
import { getOrParseType } from '../../internal/schema/GetOrParseType';
import { getTypeUnexpectedParseFailure } from '../../internal/schema/GetTypeUnexpectedParseFailure';
import { ParseContext } from '../../internal/schema/ParseContext';

export function parseTypeDeclaration(typeDeclarationArray: any[], ctx: ParseContext): UTypeDeclaration {
    if (!typeDeclarationArray.length) {
        throw new UApiSchemaParseError([
            new SchemaParseFailure(ctx.documentName, ctx.path, 'EmptyArrayDisallowed', {}),
        ]);
    }

    const basePath = ctx.path.concat([0]);
    const baseType = typeDeclarationArray[0];

    if (typeof baseType !== 'string') {
        const thisParseFailures = getTypeUnexpectedParseFailure(ctx.documentName, basePath, baseType, 'String');
        throw new UApiSchemaParseError(thisParseFailures);
    }

    const rootTypeString = baseType;

    const regexString = /^(.+?)(\?)?$/;
    const regex = new RegExp(regexString);

    const matcher = rootTypeString.match(regex);
    if (!matcher) {
        throw new UApiSchemaParseError([
            new SchemaParseFailure(ctx.documentName, basePath, 'StringRegexMatchFailed', {
                regex: regexString.toString().slice(1, -1),
            }),
        ]);
    }

    const typeName = matcher[1];
    const nullable = !!matcher[2];

    const type_ = getOrParseType(typeName, ctx.copy({ path: basePath }));

    const givenTypeParameterCount = typeDeclarationArray.length - 1;
    if (type_.getTypeParameterCount() !== givenTypeParameterCount) {
        throw new UApiSchemaParseError([
            new SchemaParseFailure(ctx.documentName, ctx.path, 'ArrayLengthUnexpected', {
                actual: typeDeclarationArray.length,
                expected: type_.getTypeParameterCount() + 1,
            }),
        ]);
    }

    const parseFailures: SchemaParseFailure[] = [];
    const typeParameters: UTypeDeclaration[] = [];
    const givenTypeParameters = typeDeclarationArray.slice(1);

    for (let index = 1; index <= givenTypeParameters.length; index++) {
        const e = givenTypeParameters[index - 1];
        const loopPath = ctx.path.concat([index]);

        if (!Array.isArray(e)) {
            const thisParseFailures = getTypeUnexpectedParseFailure(ctx.documentName, loopPath, e, 'Array');
            parseFailures.push(...thisParseFailures);
            continue;
        }

        try {
            const typeParameterTypeDeclaration = parseTypeDeclaration(e, ctx.copy({ path: loopPath }));

            typeParameters.push(typeParameterTypeDeclaration);
        } catch (e2) {
            parseFailures.push(...e2.schemaParseFailures);
        }
    }

    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures);
    }

    return new UTypeDeclaration(type_, nullable, typeParameters);
}
