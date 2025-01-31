import { MockUApiSchema } from '../../MockUApiSchema';
import { createUApiSchemaFromFileJsonMap } from './CreateUApiSchemaFromFileJsonMap';
import { getMockUApiJson } from './GetMockUApiJson';

export function createMockUApiSchemaFromFileJsonMap(jsonDocuments: Record<string, string>): MockUApiSchema {
    const finalJsonDocuments = { ...jsonDocuments };
    finalJsonDocuments['mock_'] = getMockUApiJson();

    const uApiSchema = createUApiSchemaFromFileJsonMap(finalJsonDocuments);

    return new MockUApiSchema(
        uApiSchema.original,
        uApiSchema.full,
        uApiSchema.parsed,
        uApiSchema.parsedRequestHeaders,
        uApiSchema.parsedResponseHeaders,
    );
}
