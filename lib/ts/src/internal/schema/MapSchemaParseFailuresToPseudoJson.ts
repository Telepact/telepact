import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';

export function mapSchemaParseFailuresToPseudoJson(schemaParseFailures: SchemaParseFailure[]): any[] {
    const pseudoJsonList: any[] = [];
    for (const f of schemaParseFailures) {
        const pseudoJson: any = {};
        pseudoJson.path = f.path;
        pseudoJson.reason = { [f.reason]: f.data };
        if (f.key !== null) {
            pseudoJson['key!'] = f.key;
        }
        pseudoJsonList.push(Object.assign({}, pseudoJson));
    }
    return pseudoJsonList;
}
