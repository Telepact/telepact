import { UApiSchema } from '../../UApiSchema';
import { createUApiSchemaFromFileJsonMap } from './CreateUApiSchemaFromFileJsonMap';
import { getMockUApiJson } from './GetMockUApiJson';

export function createMockUApiSchemaFromFileJsonMap(jsonDocuments: Record<string, string>): UApiSchema {
    const finalJsonDocuments = { ...jsonDocuments };
    finalJsonDocuments['mock_'] = getMockUApiJson();

    const uApiSchema = createUApiSchemaFromFileJsonMap(finalJsonDocuments);

    return uApiSchema;
}
