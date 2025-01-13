import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { UFieldDeclaration } from '../../internal/types/UFieldDeclaration';
import { UApiSchemaParseError } from '../../UApiSchemaParseError';
import { getTypeUnexpectedParseFailure } from '../../internal/schema/GetTypeUnexpectedParseFailure';
import { ParseContext } from '../../internal/schema/ParseContext';
import { parseTypeDeclaration } from './ParseTypeDeclaration';

export function parseField(fieldDeclaration: string, typeDeclarationValue: any, ctx: ParseContext): UFieldDeclaration {
    const regexString = '^([a-z][a-zA-Z0-9_]*)(!)?$';
    const regex = new RegExp(regexString);

    const matcher = fieldDeclaration.match(regex);
    if (!matcher) {
        const finalPath = [...ctx.path, fieldDeclaration];
        throw new UApiSchemaParseError([
            new SchemaParseFailure(ctx.documentName, finalPath, 'KeyRegexMatchFailed', { regex: regexString }),
        ]);
    }

    const fieldName = matcher[0];
    const optional = Boolean(matcher[2]);

    const thisPath = [...ctx.path, fieldName];

    if (!Array.isArray(typeDeclarationValue)) {
        throw new UApiSchemaParseError(
            getTypeUnexpectedParseFailure(ctx.documentName, thisPath, typeDeclarationValue, 'Array'),
        );
    }
    const typeDeclarationArray = typeDeclarationValue;

    const typeDeclaration = parseTypeDeclaration(typeDeclarationArray, ctx.copy({ path: thisPath }));

    return new UFieldDeclaration(fieldName, typeDeclaration, optional);
}
