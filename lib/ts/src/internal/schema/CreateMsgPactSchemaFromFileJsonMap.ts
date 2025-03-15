import { getInternalMsgPactJson } from './GetInternalMsgPactJson';
import { getAuthMsgPactJson } from './GetAuthMsgPactJson';
import { MsgPactSchema } from '../../MsgPactSchema';
import { parseMsgPactSchema } from './ParseMsgPactSchema';

export function createMsgPactSchemaFromFileJsonMap(jsonDocuments: Record<string, string>): MsgPactSchema {
    const finalJsonDocuments = { ...jsonDocuments };
    finalJsonDocuments['internal_'] = getInternalMsgPactJson();

    // Determine if we need to add the auth schema
    for (const json of Object.values(jsonDocuments)) {
        const regex = /"struct\.Auth_"\s*:/;
        if (regex.test(json)) {
            finalJsonDocuments['auth_'] = getAuthMsgPactJson();
            break;
        }
    }

    const msgPactSchema = parseMsgPactSchema(finalJsonDocuments);

    return msgPactSchema;
}
