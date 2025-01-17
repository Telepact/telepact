import { UFieldDeclaration } from '../../internal/types/UFieldDeclaration';
import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { UApiSchemaParseError } from '../../UApiSchemaParseError';
import { parseField } from '../../internal/schema/ParseField';
import { ParseContext } from '../../internal/schema/ParseContext';
import { getPathDocumentCoordinatesPseudoJson } from '../../internal/schema/GetPathDocumentCoordinatesPseudoJson';

export function parseStructFields(
    path: any[],
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
                const finalPath = [...path, fieldDeclaration];
                const finalOtherPath = [...path, existingField];
                const finalOtherDocumentJson = ctx.uapiSchemaDocumentNamesToJson[ctx.documentName];
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
        throw new UApiSchemaParseError(parseFailures, ctx.uapiSchemaDocumentNamesToJson);
    }

    return fields;
}
