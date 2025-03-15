import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { VFieldDeclaration } from '../types/VFieldDeclaration';
import { MsgPactSchemaParseError } from '../../MsgPactSchemaParseError';
import { getTypeUnexpectedParseFailure } from '../../internal/schema/GetTypeUnexpectedParseFailure';
import { ParseContext } from '../../internal/schema/ParseContext';
import { parseTypeDeclaration } from './ParseTypeDeclaration';

export function parseField(
    path: any[],
    fieldDeclaration: string,
    typeDeclarationValue: any,
    ctx: ParseContext,
): VFieldDeclaration {
    const regexString = '^([a-z][a-zA-Z0-9_]*)(!)?$';
    const regex = new RegExp(regexString);

    const matcher = fieldDeclaration.match(regex);
    if (!matcher) {
        const finalPath = [...path, fieldDeclaration];
        throw new MsgPactSchemaParseError(
            [new SchemaParseFailure(ctx.documentName, finalPath, 'KeyRegexMatchFailed', { regex: regexString })],
            ctx.msgpactSchemaDocumentNamesToJson,
        );
    }

    const fieldName = matcher[0];
    const optional = Boolean(matcher[2]);

    const thisPath = [...path, fieldName];

    if (!Array.isArray(typeDeclarationValue)) {
        throw new MsgPactSchemaParseError(
            getTypeUnexpectedParseFailure(ctx.documentName, thisPath, typeDeclarationValue, 'Array'),
            ctx.msgpactSchemaDocumentNamesToJson,
        );
    }
    const typeDeclarationArray = typeDeclarationValue;

    const typeDeclaration = parseTypeDeclaration(thisPath, typeDeclarationArray, ctx);

    return new VFieldDeclaration(fieldName, typeDeclaration, optional);
}
