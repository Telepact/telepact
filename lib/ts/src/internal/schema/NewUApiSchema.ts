import { UApiSchema } from '../../UApiSchema';
import { parseUapiSchema } from '../../internal/schema/ParseUApiSchema';

export function newUapiSchema(uApiSchemaFilesToJson: Record<string, string>): UApiSchema {
    return parseUapiSchema(uApiSchemaFilesToJson);
}
