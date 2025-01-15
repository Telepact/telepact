import { getInternalUApiJson } from '../../internal/schema/GetInternalUApiJson';
import { getAuthUApiJson } from '../../internal/schema/GetAuthUApiJson';
import { UApiSchema } from '../../UApiSchema';
import { parseUapiSchema } from '../../internal/schema/ParseUApiSchema';

export function createUApiSchemaFromFileJsonMap(jsonDocuments: Record<string, string>): UApiSchema {
    const finalJsonDocuments = { ...jsonDocuments };
    finalJsonDocuments['internal_'] = getInternalUApiJson();

    // Determine if we need to add the auth schema
    for (const json of Object.values(jsonDocuments)) {
        const regex = /"struct\.Auth_"\s*:/;
        if (regex.test(json)) {
            finalJsonDocuments['auth_'] = getAuthUApiJson();
            break;
        }
    }

    const uApiSchema = parseUapiSchema(finalJsonDocuments);

    return uApiSchema;
}
