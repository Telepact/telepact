import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { VTypeDeclaration } from '../types/VTypeDeclaration';
import { TelepactSchemaParseError } from '../../TelepactSchemaParseError';
import { getOrParseType } from '../../internal/schema/GetOrParseType';
import { getTypeUnexpectedParseFailure } from '../../internal/schema/GetTypeUnexpectedParseFailure';
import { ParseContext } from '../../internal/schema/ParseContext';

export function parseTypeDeclaration(path: any[], typeDeclarationArray: any[], ctx: ParseContext): VTypeDeclaration {
    if (!typeDeclarationArray.length) {
        throw new TelepactSchemaParseError(
            [new SchemaParseFailure(ctx.documentName, path, 'EmptyArrayDisallowed', {})],
            ctx.telepactSchemaDocumentNamesToJson,
        );
    }

    const basePath = path.concat([0]);
    const baseType = typeDeclarationArray[0];

    if (typeof baseType !== 'string') {
        const thisParseFailures = getTypeUnexpectedParseFailure(ctx.documentName, basePath, baseType, 'String');
        throw new TelepactSchemaParseError(thisParseFailures, ctx.telepactSchemaDocumentNamesToJson);
    }

    const rootTypeString = baseType;

    const regexString = /^(.+?)(\?)?$/;
    const regex = new RegExp(regexString);

    const matcher = rootTypeString.match(regex);
    if (!matcher) {
        throw new TelepactSchemaParseError(
            [
                new SchemaParseFailure(ctx.documentName, basePath, 'StringRegexMatchFailed', {
                    regex: regexString.toString().slice(1, -1),
                }),
            ],
            ctx.telepactSchemaDocumentNamesToJson,
        );
    }

    const typeName = matcher[1];
    const nullable = !!matcher[2];

    const type_ = getOrParseType(basePath, typeName, ctx);

    const givenTypeParameterCount = typeDeclarationArray.length - 1;
    if (type_.getTypeParameterCount() !== givenTypeParameterCount) {
        throw new TelepactSchemaParseError(
            [
                new SchemaParseFailure(ctx.documentName, path, 'ArrayLengthUnexpected', {
                    actual: typeDeclarationArray.length,
                    expected: type_.getTypeParameterCount() + 1,
                }),
            ],
            ctx.telepactSchemaDocumentNamesToJson,
        );
    }

    const parseFailures: SchemaParseFailure[] = [];
    const typeParameters: VTypeDeclaration[] = [];
    const givenTypeParameters = typeDeclarationArray.slice(1);

    for (let index = 1; index <= givenTypeParameters.length; index++) {
        const e = givenTypeParameters[index - 1];
        const loopPath = path.concat([index]);

        if (!Array.isArray(e)) {
            const thisParseFailures = getTypeUnexpectedParseFailure(ctx.documentName, loopPath, e, 'Array');
            parseFailures.push(...thisParseFailures);
            continue;
        }

        try {
            const typeParameterTypeDeclaration = parseTypeDeclaration(loopPath, e, ctx);

            typeParameters.push(typeParameterTypeDeclaration);
        } catch (e2) {
            parseFailures.push(...e2.schemaParseFailures);
        }
    }

    if (parseFailures.length > 0) {
        throw new TelepactSchemaParseError(parseFailures, ctx.telepactSchemaDocumentNamesToJson);
    }

    return new VTypeDeclaration(type_, nullable, typeParameters);
}
