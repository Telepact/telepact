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

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import io.github.telepact.TelepactSchemaParseError;

public class CatchErrorCollisions {
    public static void catchErrorCollisions(Map<String, List<Object>> telepactSchemaNameToPseudoJson, Set<String> errorKeys,
            Map<String, Integer> keysToIndex, Map<String, String> schemaKeysToDocumentName,
            Map<String, String> documentNamesToJson) {
        List<SchemaParseFailure> parseFailures = new ArrayList<>();

        var errorKeysList = new ArrayList<>(errorKeys);

        errorKeysList.sort((k1, k2) -> {
            var documentName1 = schemaKeysToDocumentName.get(k1);
            var documentName2 = schemaKeysToDocumentName.get(k2);
            if (!documentName1.equals(documentName2)) {
                return documentName1.compareTo(documentName2);
            } else {
                var index1 = keysToIndex.get(k1);
                var index2 = keysToIndex.get(k2);
                return index1 - index2;
            }
        });

        for (var i = 0; i < errorKeysList.size(); i++) {
            for (var j = i + 1; j < errorKeysList.size(); j++) {
                var defKey = errorKeysList.get(i);
                var otherDefKey = errorKeysList.get(j);

                int index = keysToIndex.get(defKey);
                int otherIndex = keysToIndex.get(otherDefKey);

                var documentName = schemaKeysToDocumentName.get(defKey);
                var otherDocumentName = schemaKeysToDocumentName.get(otherDefKey);

                var telepactSchemaPseudoJson = telepactSchemaNameToPseudoJson.get(documentName);
                var otherTelepactSchemaPseudoJson = telepactSchemaNameToPseudoJson.get(otherDocumentName);

                var def = (Map<String, Object>) telepactSchemaPseudoJson.get(index);
                var otherDef = (Map<String, Object>) otherTelepactSchemaPseudoJson.get(otherIndex);

                var errDef = (List<Object>) def.get(defKey);
                var otherErrDef = (List<Object>) otherDef.get(otherDefKey);

                for (int k = 0; k < errDef.size(); k++) {
                    var thisErrDef = (Map<String, Object>) errDef.get(k);
                    var thisErrDefKeys = new HashSet<>(thisErrDef.keySet());
                    thisErrDefKeys.remove("///");

                    for (int l = 0; l < otherErrDef.size(); l++) {
                        var thisOtherErrDef = (Map<String, Object>) otherErrDef.get(l);
                        var thisOtherErrDefKeys = new HashSet<>(thisOtherErrDef.keySet());
                        thisOtherErrDefKeys.remove("///");

                        if (thisErrDefKeys.equals(thisOtherErrDefKeys)) {
                            String thisErrorDefKey = thisErrDefKeys.iterator().next();
                            String thisOtherErrorDefKey = thisOtherErrDefKeys.iterator().next();
                            List<Object> finalThisPath = List.of(index, defKey, k, thisErrorDefKey);
                            var finalThisDocument = documentNamesToJson.get(documentName);
                            var finalThisLocation = GetPathDocumentCoordinatesPseudoJson
                                    .getPathDocumentCoordinatesPseudoJson(finalThisPath, finalThisDocument);
                            parseFailures.add(new SchemaParseFailure(
                                    otherDocumentName,
                                    List.of(otherIndex, otherDefKey, l, thisOtherErrorDefKey),
                                    "PathCollision",
                                    Map.of("document", documentName, "path",
                                            finalThisPath, "location", finalThisLocation)));
                        }
                    }
                }
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new TelepactSchemaParseError(parseFailures, documentNamesToJson);
        }
    }
}
