import { getInternalTelepactJson } from './GetInternalTelepactJson';
import { getAuthTelepactJson } from './GetAuthTelepactJson';
import { TelepactSchema } from '../../TelepactSchema';
import { parseTelepactSchema } from './ParseTelepactSchema';

export function createTelepactSchemaFromFileJsonMap(jsonDocuments: Record<string, string>): TelepactSchema {
    const finalJsonDocuments = { ...jsonDocuments };
    finalJsonDocuments['internal_'] = getInternalTelepactJson();

    // Determine if we need to add the auth schema
    for (const json of Object.values(jsonDocuments)) {
        const regex = /"struct\.Auth_"\s*:/;
        if (regex.test(json)) {
            finalJsonDocuments['auth_'] = getAuthTelepactJson();
            break;
        }
    }

    const telepactSchema = parseTelepactSchema(finalJsonDocuments);

    return telepactSchema;
}
