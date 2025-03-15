import { MockMsgPactSchema } from '../../MockMsgPactSchema';
import { createMsgPactSchemaFromFileJsonMap } from './CreateMsgPactSchemaFromFileJsonMap';
import { getMockMsgPactJson } from './GetMockMsgPactJson';

export function createMockMsgPactSchemaFromFileJsonMap(jsonDocuments: Record<string, string>): MockMsgPactSchema {
    const finalJsonDocuments = { ...jsonDocuments };
    finalJsonDocuments['mock_'] = getMockMsgPactJson();

    const msgPactSchema = createMsgPactSchemaFromFileJsonMap(finalJsonDocuments);

    return new MockMsgPactSchema(
        msgPactSchema.original,
        msgPactSchema.full,
        msgPactSchema.parsed,
        msgPactSchema.parsedRequestHeaders,
        msgPactSchema.parsedResponseHeaders,
    );
}
