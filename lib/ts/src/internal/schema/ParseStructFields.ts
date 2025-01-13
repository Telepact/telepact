import { UFieldDeclaration } from '../../internal/types/UFieldDeclaration';
import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { UApiSchemaParseError } from '../../UApiSchemaParseError';
import { parseField } from '../../internal/schema/ParseField';
import { ParseContext } from '../../internal/schema/ParseContext';

export function parseStructFields(
    referenceStruct: { [key: string]: any },
    ctx: ParseContext,
): { [key: string]: UFieldDeclaration } {
    const parseFailures: SchemaParseFailure[] = [];
    const fields: { [key: string]: UFieldDeclaration } = {};

    for (const fieldDeclaration in referenceStruct) {
        for (const existingField in fields) {
            const existingFieldNoOpt = existingField.split('!')[0];
            const fieldNoOpt = fieldDeclaration.split('!')[0];
            if (fieldNoOpt === existingFieldNoOpt) {
                const finalPath = [...ctx.path, fieldDeclaration];
                const finalOtherPath = [...ctx.path, existingField];
                parseFailures.push(
                    new SchemaParseFailure(ctx.documentName, finalPath, 'PathCollision', {
                        document: ctx.documentName,
                        path: finalOtherPath,
                    }),
                );
            }
        }

        try {
            const parsedField = parseField(fieldDeclaration, referenceStruct[fieldDeclaration], ctx);
            const fieldName = parsedField.fieldName;
            fields[fieldName] = parsedField;
        } catch (e) {
            if (e instanceof UApiSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            } else {
                throw e;
            }
        }
    }

    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures);
    }

    return fields;
}
