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
import io.github.telepact.internal.types.TArray;
import io.github.telepact.internal.types.TFieldDeclaration;
import io.github.telepact.internal.types.TObject;
import io.github.telepact.internal.types.TStruct;
import io.github.telepact.internal.types.TType;
import io.github.telepact.internal.types.TTypeDeclaration;
import io.github.telepact.internal.types.TUnion;

public class ValidateTypeTermination {
    private static boolean typeDeclarationTerminates(TTypeDeclaration typeDeclaration, Set<String> terminatingTypeNames) {
        if (typeDeclaration.nullable) {
            return true;
        }

        if (typeDeclaration.type instanceof TArray || typeDeclaration.type instanceof TObject) {
            return true;
        }

        if (typeDeclaration.type instanceof TStruct structType) {
            return terminatingTypeNames.contains(structType.name);
        }

        if (typeDeclaration.type instanceof TUnion unionType) {
            return terminatingTypeNames.contains(unionType.name);
        }

        return true;
    }

    private static boolean structFieldsTerminate(Map<String, TFieldDeclaration> fields, Set<String> terminatingTypeNames) {
        return fields.values().stream().allMatch(
                field -> field.optional || typeDeclarationTerminates(field.typeDeclaration, terminatingTypeNames));
    }

    private static boolean typeTerminates(TType type, Set<String> terminatingTypeNames) {
        if (type instanceof TStruct structType) {
            return structFieldsTerminate(structType.fields, terminatingTypeNames);
        }

        if (type instanceof TUnion unionType) {
            return unionType.tags.values().stream()
                    .anyMatch(tag -> structFieldsTerminate(tag.fields, terminatingTypeNames));
        }

        return true;
    }

    public static void validateTypeTermination(
            Map<String, TType> parsedTypes,
            Map<String, String> schemaKeysToDocumentName,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, String> telepactSchemaNameToJson) {
        final var terminatingTypeNames = new HashSet<String>();

        var changed = true;
        while (changed) {
            changed = false;
            for (var entry : parsedTypes.entrySet()) {
                if (terminatingTypeNames.contains(entry.getKey())) {
                    continue;
                }

                if (typeTerminates(entry.getValue(), terminatingTypeNames)) {
                    terminatingTypeNames.add(entry.getKey());
                    changed = true;
                }
            }
        }

        final var parseFailures = new ArrayList<SchemaParseFailure>();
        for (var entry : schemaKeysToDocumentName.entrySet()) {
            final var schemaKey = entry.getKey();
            if (schemaKey.startsWith("info.") || schemaKey.startsWith("headers.") || schemaKey.startsWith("errors.")) {
                continue;
            }

            final List<String> rootTypeNames = new ArrayList<>(List.of(schemaKey));
            if (schemaKey.startsWith("fn.")) {
                rootTypeNames.add(schemaKey + ".->");
            }

            for (var rootTypeName : rootTypeNames) {
                if (parsedTypes.containsKey(rootTypeName) && !terminatingTypeNames.contains(rootTypeName)) {
                    final List<Object> path = rootTypeName.endsWith(".->")
                            ? List.of(schemaKeysToIndex.get(schemaKey), "->")
                            : List.of(schemaKeysToIndex.get(schemaKey), schemaKey);
                    parseFailures.add(new SchemaParseFailure(
                            entry.getValue(),
                            path,
                            "RecursiveTypeUnterminated",
                            Map.of()));
                }
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new TelepactSchemaParseError(parseFailures, telepactSchemaNameToJson);
        }
    }
}
