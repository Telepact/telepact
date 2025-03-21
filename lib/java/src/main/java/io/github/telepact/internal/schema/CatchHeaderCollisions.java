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

import static io.github.telepact.internal.schema.GetPathDocumentCoordinatesPseudoJson.getPathDocumentCoordinatesPseudoJson;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import io.github.telepact.TelepactSchemaParseError;

public class CatchHeaderCollisions {

    public static void catchHeaderCollisions(
            Map<String, List<Object>> telepactSchemaNameToPseudoJson,
            Set<String> headerKeys,
            Map<String, Integer> keysToIndex,
            Map<String, String> schemaKeysToDocumentNames,
            Map<String, String> documentNamesToJson) {
        List<SchemaParseFailure> parseFailures = new ArrayList<>();

        List<String> headerKeysList = new ArrayList<>(headerKeys);

        headerKeysList.sort((k1, k2) -> {
            String documentName1 = schemaKeysToDocumentNames.get(k1);
            String documentName2 = schemaKeysToDocumentNames.get(k2);
            if (!documentName1.equals(documentName2)) {
                return documentName1.compareTo(documentName2);
            } else {
                int index1 = keysToIndex.get(k1);
                int index2 = keysToIndex.get(k2);
                return Integer.compare(index1, index2);
            }
        });

        for (int i = 0; i < headerKeysList.size(); i++) {
            for (int j = i + 1; j < headerKeysList.size(); j++) {
                String defKey = headerKeysList.get(i);
                String otherDefKey = headerKeysList.get(j);

                int index = keysToIndex.get(defKey);
                int otherIndex = keysToIndex.get(otherDefKey);

                String documentName = schemaKeysToDocumentNames.get(defKey);
                String otherDocumentName = schemaKeysToDocumentNames.get(otherDefKey);

                List<Object> telepactSchemaPseudoJson = telepactSchemaNameToPseudoJson.get(documentName);
                List<Object> otherTelepactSchemaPseudoJson = telepactSchemaNameToPseudoJson.get(otherDocumentName);

                Map<String, Object> def = (Map<String, Object>) telepactSchemaPseudoJson.get(index);
                Map<String, Object> otherDef = (Map<String, Object>) otherTelepactSchemaPseudoJson.get(otherIndex);

                Map<String, Object> headerDef = (Map<String, Object>) def.get(defKey);
                Map<String, Object> otherHeaderDef = (Map<String, Object>) otherDef.get(otherDefKey);

                Set<String> headerCollisions = new HashSet<>(headerDef.keySet());
                headerCollisions.retainAll(otherHeaderDef.keySet());
                for (String headerCollision : headerCollisions) {
                    List<Object> thisPath = Arrays.asList(index, defKey, headerCollision);
                    String thisDocumentJson = documentNamesToJson.get(documentName);
                    Object thisLocation = getPathDocumentCoordinatesPseudoJson(thisPath, thisDocumentJson);
                    parseFailures.add(new SchemaParseFailure(
                            otherDocumentName,
                            Arrays.asList(otherIndex, otherDefKey, headerCollision),
                            "PathCollision",
                            Map.of("document", documentName, "path", thisPath, "location", thisLocation)));
                }

                Map<String, Object> resHeaderDef = (Map<String, Object>) def.get("->");
                Map<String, Object> otherResHeaderDef = (Map<String, Object>) otherDef.get("->");

                Set<String> resHeaderCollisions = new HashSet<>(resHeaderDef.keySet());
                resHeaderCollisions.retainAll(otherResHeaderDef.keySet());
                for (String resHeaderCollision : resHeaderCollisions) {
                    List<Object> thisPath = Arrays.asList(index, "->", resHeaderCollision);
                    String thisDocumentJson = documentNamesToJson.get(documentName);
                    Object thisLocation = getPathDocumentCoordinatesPseudoJson(thisPath, thisDocumentJson);
                    parseFailures.add(new SchemaParseFailure(
                            otherDocumentName,
                            Arrays.asList(otherIndex, "->", resHeaderCollision),
                            "PathCollision",
                            Map.of("document", documentName, "path", thisPath, "location", thisLocation)));
                }
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new TelepactSchemaParseError(parseFailures, documentNamesToJson);
        }
    }
}