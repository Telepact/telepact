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

package io.github.telepact.internal.schema;

import static io.github.telepact.internal.schema.GetAuthTelepactJson.getAuthTelepactJson;
import static io.github.telepact.internal.schema.GetInternalTelepactJson.getInternalTelepactJson;
import static io.github.telepact.internal.schema.ParseTelepactSchema.parseTelepactSchema;

import java.util.HashMap;
import java.util.Map;
import java.util.regex.Pattern;

import io.github.telepact.TelepactSchema;

public class CreateTelepactSchemaFromFileJsonMap {
    public static TelepactSchema createTelepactSchemaFromFileJsonMap(Map<String, String> jsonDocuments) {
        var finalJsonDocuments = new HashMap<String, String>();
        finalJsonDocuments.putAll(jsonDocuments);
        finalJsonDocuments.put("internal_", getInternalTelepactJson());

        // Determine if we need to add the auth schema
        for (var json : jsonDocuments.values()) {
            var regex = Pattern.compile("\"struct\\.Auth_\"\\s*:");
            var matcher = regex.matcher(json);
            if (matcher.find()) {
                finalJsonDocuments.put("auth_", getAuthTelepactJson());
                break;
            }
        }

        var telepactSchema = parseTelepactSchema(finalJsonDocuments);

        return telepactSchema;
    }
}
