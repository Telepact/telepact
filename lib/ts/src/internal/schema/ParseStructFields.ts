import { UFieldDeclaration } from '../../internal/types/UFieldDeclaration';
import { UType } from '../../internal/types/UType';
import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { UApiSchemaParseError } from '../../UApiSchemaParseError';
import { parseField } from '../../internal/schema/ParseField';

export function parseStructFields(
    referenceStruct: { [key: string]: any },
    path: any[],
    typeParameterCount: number,
    uapiSchemaPseudoJson: any[],
    schemaKeysToIndex: { [key: string]: number },
    parsedTypes: { [key: string]: UType },
    allParseFailures: SchemaParseFailure[],
    failedTypes: Set<string>,
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
                parseFailures.push(new SchemaParseFailure(finalPath, 'PathCollision', { other: finalOtherPath }, null));
            }
        }

        try {
            const parsedField = parseField(
                path,
                fieldDeclaration,
                referenceStruct[fieldDeclaration],
                typeParameterCount,
                uapiSchemaPseudoJson,
                schemaKeysToIndex,
                parsedTypes,
                allParseFailures,
                failedTypes,
            );
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
