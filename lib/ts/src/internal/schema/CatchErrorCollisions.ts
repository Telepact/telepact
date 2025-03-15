import { MsgPactSchemaParseError } from '../../MsgPactSchemaParseError';
import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { getPathDocumentCoordinatesPseudoJson } from '../../internal/schema/GetPathDocumentCoordinatesPseudoJson';

export function catchErrorCollisions(
    msgPactSchemaNameToPseudoJson: Record<string, any[]>,
    errorKeys: Set<string>,
    keysToIndex: Record<string, number>,
    schemaKeysToDocumentNames: Record<string, string>,
    documentNamesToJson: Record<string, string>,
): void {
    const parseFailures: SchemaParseFailure[] = [];

    const errorKeysList = [...errorKeys];

    errorKeysList.sort((k1, k2) => {
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

    for (let i = 0; i < errorKeysList.length; i++) {
        for (let j = i + 1; j < errorKeysList.length; j++) {
            const defKey = errorKeysList[i];
            const otherDefKey = errorKeysList[j];

            const index = keysToIndex[defKey];
            const otherIndex = keysToIndex[otherDefKey];

            const documentName = schemaKeysToDocumentNames[defKey];
            const otherDocumentName = schemaKeysToDocumentNames[otherDefKey];

            const msgPactSchemaPseudoJson = msgPactSchemaNameToPseudoJson[documentName];
            const otherMsgPactSchemaPseudoJson = msgPactSchemaNameToPseudoJson[otherDocumentName];

            const def = msgPactSchemaPseudoJson[index] as Record<string, object>;
            const otherDef = otherMsgPactSchemaPseudoJson[otherIndex] as Record<string, object>;

            const errDef = def[defKey] as object[];
            const otherErrDef = otherDef[otherDefKey] as object[];

            for (let k = 0; k < errDef.length; k++) {
                const thisErrDef = errDef[k] as Record<string, object>;
                const thisErrDefKeys = new Set(Object.keys(thisErrDef));
                thisErrDefKeys.delete('///');

                for (let l = 0; l < otherErrDef.length; l++) {
                    const thisOtherErrDef = otherErrDef[l] as Record<string, object>;
                    const thisOtherErrDefKeys = new Set(Object.keys(thisOtherErrDef));
                    thisOtherErrDefKeys.delete('///');

                    if (
                        thisErrDefKeys.size === thisOtherErrDefKeys.size &&
                        [...thisErrDefKeys].every((key) => thisOtherErrDefKeys.has(key))
                    ) {
                        const thisErrorDefKey = thisErrDefKeys.values().next().value as string;
                        const thisOtherErrorDefKey = thisOtherErrDefKeys.values().next().value as string;
                        const thisPath = [index, defKey, k, thisErrorDefKey];
                        const thisDocumentJson = documentNamesToJson[documentName];
                        const thisLocation = getPathDocumentCoordinatesPseudoJson(thisPath, thisDocumentJson);
                        parseFailures.push(
                            new SchemaParseFailure(
                                otherDocumentName,
                                [otherIndex, otherDefKey, l, thisOtherErrorDefKey],
                                'PathCollision',
                                { document: documentName, path: thisPath, location: thisLocation },
                            ),
                        );
                    }
                }
            }
        }
    }

    if (parseFailures.length > 0) {
        throw new MsgPactSchemaParseError(parseFailures, documentNamesToJson);
    }
}
