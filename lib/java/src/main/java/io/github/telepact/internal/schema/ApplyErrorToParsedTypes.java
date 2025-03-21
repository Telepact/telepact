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
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;

import io.github.telepact.TelepactSchemaParseError;
import io.github.telepact.internal.types.VError;
import io.github.telepact.internal.types.VFn;
import io.github.telepact.internal.types.VType;

public class ApplyErrorToParsedTypes {
    public static void applyErrorToParsedTypes(VError error,
            Map<String, VType> parsedTypes, Map<String, String> schemaKeysToDocumentNames,
            Map<String, Integer> schemaKeysToIndex, Map<String, String> documentNamesToJson) {
        var parseFailures = new ArrayList<SchemaParseFailure>();

        var errorKey = error.name;
        var errorIndex = schemaKeysToIndex.get(errorKey);
        var documentName = schemaKeysToDocumentNames.get(errorKey);

        for (var entry : parsedTypes.entrySet()) {
            var parsedTypeName = entry.getKey();
            var parsedType = entry.getValue();

            if (!(parsedType instanceof VFn)) {
                continue;
            }

            var f = (VFn) parsedType;
            var fnName = f.name;
            var regex = Pattern.compile(f.errorsRegex);
            var fnResult = f.result;
            var fnResultTags = fnResult.tags;
            var errorErrors = error.errors;
            var errorTags = errorErrors.tags;

            var matcher = regex.matcher(errorKey);
            if (!matcher.matches()) {
                continue;
            }

            for (var errorTagEntry : errorTags.entrySet()) {
                var errorTagName = errorTagEntry.getKey();
                var errorTag = errorTagEntry.getValue();
                var newKey = errorTagName;

                if (fnResultTags.containsKey(newKey)) {
                    var otherPathIndex = schemaKeysToIndex.get(fnName);
                    var errorTagIndex = error.errors.tagIndices.get(newKey);
                    var otherDocumentName = schemaKeysToDocumentNames.get(fnName);
                    var fnErrorTagIndex = f.result.tagIndices.get(newKey);
                    List<Object> otherFinalPath = List.of(otherPathIndex, "->", fnErrorTagIndex, newKey);
                    var otherDocumentJson = documentNamesToJson.get(otherDocumentName);
                    var otherLocationPseudoJson = GetPathDocumentCoordinatesPseudoJson
                            .getPathDocumentCoordinatesPseudoJson(
                                    otherFinalPath, otherDocumentJson);
                    parseFailures.add(new SchemaParseFailure(documentName,
                            List.of(errorIndex, errorKey, errorTagIndex, newKey),
                            "PathCollision",
                            Map.of("document", otherDocumentName, "path",
                                    otherFinalPath, "location", otherLocationPseudoJson)));
                }
                fnResultTags.put(newKey, errorTag);
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new TelepactSchemaParseError(parseFailures, documentNamesToJson);
        }
    }
}
