import { MockTelepactSchema } from '../../MockTelepactSchema';
import { createTelepactSchemaFromFileJsonMap } from './CreateTelepactSchemaFromFileJsonMap';
import { getMockTelepactJson } from './GetMockTelepactJson';

export function createMockTelepactSchemaFromFileJsonMap(jsonDocuments: Record<string, string>): MockTelepactSchema {
    const finalJsonDocuments = { ...jsonDocuments };
    finalJsonDocuments['mock_'] = getMockTelepactJson();

    const telepactSchema = createTelepactSchemaFromFileJsonMap(finalJsonDocuments);

    return new MockTelepactSchema(
        telepactSchema.original,
        telepactSchema.full,
        telepactSchema.parsed,
        telepactSchema.parsedRequestHeaders,
        telepactSchema.parsedResponseHeaders,
    );
}
