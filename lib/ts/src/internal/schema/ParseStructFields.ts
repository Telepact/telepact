import { VFieldDeclaration } from '../types/VFieldDeclaration';
import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { MsgPactSchemaParseError } from '../../MsgPactSchemaParseError';
import { parseField } from '../../internal/schema/ParseField';
import { ParseContext } from '../../internal/schema/ParseContext';
import { getPathDocumentCoordinatesPseudoJson } from '../../internal/schema/GetPathDocumentCoordinatesPseudoJson';

export function parseStructFields(
    path: any[],
    referenceStruct: { [key: string]: any },
    ctx: ParseContext,
): { [key: string]: VFieldDeclaration } {
    const parseFailures: SchemaParseFailure[] = [];
    const fields: { [key: string]: VFieldDeclaration } = {};

    for (const fieldDeclaration in referenceStruct) {
        for (const existingField in fields) {
            const existingFieldNoOpt = existingField.split('!')[0];
            const fieldNoOpt = fieldDeclaration.split('!')[0];
            if (fieldNoOpt === existingFieldNoOpt) {
                const finalPath = [...path, fieldDeclaration];
                const finalOtherPath = [...path, existingField];
                const finalOtherDocumentJson = ctx.msgpactSchemaDocumentNamesToJson[ctx.documentName];
                const finalOtherLocation = getPathDocumentCoordinatesPseudoJson(finalOtherPath, finalOtherDocumentJson);
                parseFailures.push(
                    new SchemaParseFailure(ctx.documentName, finalPath, 'PathCollision', {
                        document: ctx.documentName,
                        location: finalOtherLocation,
                        path: finalOtherPath,
                    }),
                );
            }
        }

        try {
            const parsedField = parseField(path, fieldDeclaration, referenceStruct[fieldDeclaration], ctx);
            const fieldName = parsedField.fieldName;
            fields[fieldName] = parsedField;
        } catch (e) {
            if (e instanceof MsgPactSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            } else {
                throw e;
            }
        }
    }

    if (parseFailures.length > 0) {
        throw new MsgPactSchemaParseError(parseFailures, ctx.msgpactSchemaDocumentNamesToJson);
    }

    return fields;
}
