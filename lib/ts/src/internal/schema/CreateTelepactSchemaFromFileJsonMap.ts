//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

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
            finalJsonDocuments['@auth_'] = getAuthTelepactJson();
            break;
        }
    }

    const telepactSchema = parseTelepactSchema(finalJsonDocuments);

    return telepactSchema;
}
