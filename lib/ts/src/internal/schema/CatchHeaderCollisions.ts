import { TelepactSchemaParseError } from '../../TelepactSchemaParseError';
import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { getPathDocumentCoordinatesPseudoJson } from '../../internal/schema/GetPathDocumentCoordinatesPseudoJson';

export function catchHeaderCollisions(
    telepactSchemaNameToPseudoJson: Record<string, any[]>,
    headerKeys: Set<string>,
    keysToIndex: Record<string, number>,
    schemaKeysToDocumentNames: Record<string, string>,
    documentNamesToJson: Record<string, string>,
): void {
    const parseFailures: SchemaParseFailure[] = [];

    const headerKeysList = [...headerKeys];

    headerKeysList.sort((k1, k2) => {
        const documentName1 = schemaKeysToDocumentNames[k1];
        const documentName2 = schemaKeysToDocumentNames[k2];
        if (documentName1 !== documentName2) {
            return documentName1.localeCompare(documentName2);
        } else {
            const index1 = keysToIndex[k1];
            const index2 = keysToIndex[k2];
            return index1 - index2;
        }
    });

    for (let i = 0; i < headerKeysList.length; i++) {
        for (let j = i + 1; j < headerKeysList.length; j++) {
            const defKey = headerKeysList[i];
            const otherDefKey = headerKeysList[j];

            const index = keysToIndex[defKey];
            const otherIndex = keysToIndex[otherDefKey];

            const documentName = schemaKeysToDocumentNames[defKey];
            const otherDocumentName = schemaKeysToDocumentNames[otherDefKey];

            const telepactSchemaPseudoJson = telepactSchemaNameToPseudoJson[documentName];
            const otherTelepactSchemaPseudoJson = telepactSchemaNameToPseudoJson[otherDocumentName];

            const def = telepactSchemaPseudoJson[index] as Record<string, object>;
            const otherDef = otherTelepactSchemaPseudoJson[otherIndex] as Record<string, object>;

            const headerDef = def[defKey] as Record<string, object>;
            const otherHeaderDef = otherDef[otherDefKey] as Record<string, object>;

            const headerCollisions = Object.keys(headerDef).filter((k) => k in otherHeaderDef);
            for (const headerCollision of headerCollisions) {
                const thisPath = [index, defKey, headerCollision];
                const thisDocumentJson = documentNamesToJson[documentName];
                const thisLocation = getPathDocumentCoordinatesPseudoJson(thisPath, thisDocumentJson);
                parseFailures.push(
                    new SchemaParseFailure(
                        otherDocumentName,
                        [otherIndex, otherDefKey, headerCollision],
                        'PathCollision',
                        { document: documentName, path: thisPath, location: thisLocation },
                    ),
                );
            }

            const resHeaderDef = def['->'] as Record<string, object>;
            const otherResHeaderDef = otherDef['->'] as Record<string, object>;

            const resHeaderCollisions = Object.keys(resHeaderDef).filter((k) => k in otherResHeaderDef);
            for (const resHeaderCollision of resHeaderCollisions) {
                const thisPath = [index, '->', resHeaderCollision];
                const thisDocumentJson = documentNamesToJson[documentName];
                const thisLocation = getPathDocumentCoordinatesPseudoJson(thisPath, thisDocumentJson);
                parseFailures.push(
                    new SchemaParseFailure(otherDocumentName, [otherIndex, '->', resHeaderCollision], 'PathCollision', {
                        document: documentName,
                        path: thisPath,
                        location: thisLocation,
                    }),
                );
            }
        }
    }

    if (parseFailures.length > 0) {
        throw new TelepactSchemaParseError(parseFailures, documentNamesToJson);
    }
}
