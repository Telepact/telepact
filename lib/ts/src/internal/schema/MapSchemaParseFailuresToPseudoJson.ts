import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';

export function mapSchemaParseFailuresToPseudoJson(schemaParseFailures: SchemaParseFailure[]): any[] {
    const pseudoJsonList: any[] = [];
    for (const f of schemaParseFailures) {
        const pseudoJson: any = {};
        pseudoJson.document = f.documentName;
        pseudoJson.path = f.path;
        pseudoJson.reason = { [f.reason]: f.data };
        pseudoJsonList.push(Object.assign({}, pseudoJson));
    }
    return pseudoJsonList;
}
