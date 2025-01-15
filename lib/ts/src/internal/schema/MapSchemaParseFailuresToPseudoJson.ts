import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { getPathDocumentCoordinatesPseudoJson } from './GetPathDocumentCoordinatesPseudoJson';

export function mapSchemaParseFailuresToPseudoJson(
    schemaParseFailures: SchemaParseFailure[],
    documentNamesToJson: Record<string, string>,
): any[] {
    const pseudoJsonList: any[] = [];
    for (const f of schemaParseFailures) {
        const documentJson = documentNamesToJson[f.documentName];
        const location = getPathDocumentCoordinatesPseudoJson(f.path, documentJson);
        const pseudoJson: any = {};
        pseudoJson.document = f.documentName;
        pseudoJson.location = location;
        pseudoJson.path = f.path;
        pseudoJson.reason = { [f.reason]: f.data };
        pseudoJsonList.push(Object.assign({}, pseudoJson));
    }
    return pseudoJsonList;
}
