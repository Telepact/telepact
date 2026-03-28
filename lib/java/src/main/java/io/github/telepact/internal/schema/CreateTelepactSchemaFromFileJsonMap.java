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

import static io.github.telepact.internal.schema.FindSchemaKey.findSchemaKey;
import static io.github.telepact.internal.schema.GetAuthTelepactJson.getAuthTelepactJson;
import static io.github.telepact.internal.schema.GetInternalTelepactJson.getInternalTelepactJson;
import static io.github.telepact.internal.schema.ParseTelepactSchema.parseTelepactSchema;

import java.io.IOException;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import io.github.telepact.TelepactSchema;
import io.github.telepact.internal.schema.DocumentLocators.SchemaDocumentMap;

public class CreateTelepactSchemaFromFileJsonMap {
    public static TelepactSchema createTelepactSchemaFromFileJsonMap(Map<String, String> jsonDocuments) {
        var finalJsonDocuments = new SchemaDocumentMap(jsonDocuments);
        final var internalJson = getInternalTelepactJson();
        if (!hasBundledDefinitions(jsonDocuments, "internal_", internalJson)) {
            finalJsonDocuments.put("internal_", internalJson);
        }

        // Determine if we need to add the auth schema
        final var authJson = getAuthTelepactJson();
        for (var json : jsonDocuments.values()) {
            var regex = Pattern.compile("\"union\\.Auth_\"\\s*:");
            var matcher = regex.matcher(json);
            if (matcher.find()) {
                if (!hasBundledDefinitions(jsonDocuments, "auth_", authJson)) {
                    finalJsonDocuments.put("auth_", authJson);
                }
                break;
            }
        }

        var telepactSchema = parseTelepactSchema(finalJsonDocuments);

        return telepactSchema;
    }

    private static boolean hasBundledDefinitions(Map<String, String> jsonDocuments, String bundledDocumentName,
            String bundledJson) {
        final var bundledKeys = collectSchemaKeys(Map.of(bundledDocumentName, bundledJson));
        if (bundledKeys == null) {
            return false;
        }

        final var providedKeys = collectSchemaKeys(jsonDocuments);
        if (providedKeys == null) {
            return false;
        }

        return providedKeys.containsAll(bundledKeys);
    }

    private static Set<String> collectSchemaKeys(Map<String, String> jsonDocuments) {
        final var objectMapper = new ObjectMapper();
        final var schemaKeys = new HashSet<String>();

        for (var entry : jsonDocuments.entrySet()) {
            final Object pseudoJsonValue;
            try {
                pseudoJsonValue = objectMapper.readValue(entry.getValue(), new TypeReference<>() {
                });
            } catch (IOException e) {
                return null;
            }

            if (!(pseudoJsonValue instanceof List<?> pseudoJson)) {
                return null;
            }

            for (int index = 0; index < pseudoJson.size(); index += 1) {
                final var definition = pseudoJson.get(index);
                if (!(definition instanceof Map<?, ?>)) {
                    continue;
                }

                try {
                    schemaKeys.add(findSchemaKey(
                            entry.getKey(),
                            (Map<String, Object>) definition,
                            index,
                            jsonDocuments));
                } catch (RuntimeException e) {
                    return null;
                }
            }
        }

        return schemaKeys;
    }
}
