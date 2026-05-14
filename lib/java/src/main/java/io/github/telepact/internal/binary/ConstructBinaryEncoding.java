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

package io.github.telepact.internal.binary;

import static io.github.telepact.internal.binary.CreateChecksum.createChecksum;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeSet;

import io.github.telepact.TelepactSchema;
import io.github.telepact.internal.types.TArray;
import io.github.telepact.internal.types.TObject;
import io.github.telepact.internal.types.TStruct;
import io.github.telepact.internal.types.TTypeDeclaration;
import io.github.telepact.internal.types.TUnion;

public class ConstructBinaryEncoding {

    private static List<String> traceType(TTypeDeclaration typeDeclaration) {
        final var thisAllKeys = new ArrayList<String>();

        if (typeDeclaration.type instanceof TArray) {
            final var theseKeys2 = traceType(typeDeclaration.typeParameters.get(0));
            thisAllKeys.addAll(theseKeys2);
        } else if (typeDeclaration.type instanceof TObject) {
            final var theseKeys2 = traceType(typeDeclaration.typeParameters.get(0));
            thisAllKeys.addAll(theseKeys2);
        } else if (typeDeclaration.type instanceof TStruct s) {
            final var structFields = s.fields;
            for (final var entry : structFields.entrySet()) {
                final var structFieldKey = entry.getKey();
                final var structField = entry.getValue();
                thisAllKeys.add(structFieldKey);
                final var moreKeys = traceType(structField.typeDeclaration);
                thisAllKeys.addAll(moreKeys);
            }
        } else if (typeDeclaration.type instanceof TUnion u) {
            final var unionTags = u.tags;
            for (final var entry : unionTags.entrySet()) {
                final var tagKey = entry.getKey();
                final var tagValue = entry.getValue();
                thisAllKeys.add(tagKey);
                final var structFields = tagValue.fields;
                for (final var fieldEntry : structFields.entrySet()) {
                    final var structFieldKey = fieldEntry.getKey();
                    final var structField = fieldEntry.getValue();
                    thisAllKeys.add(structFieldKey);
                    final var moreKeys = traceType(structField.typeDeclaration);
                    thisAllKeys.addAll(moreKeys);
                }
            }
        }

        return thisAllKeys;
    }

    private static Map<String, Object> compileTypeDescriptor(TTypeDeclaration typeDeclaration, Map<String, Integer> encodeMap, java.util.Set<String> visitedTypeNames) {
        if (typeDeclaration.type instanceof TArray) {
            return Map.of("t", "a", "i", compileTypeDescriptor(typeDeclaration.typeParameters.get(0), encodeMap, visitedTypeNames));
        } else if (typeDeclaration.type instanceof TObject) {
            return Map.of("t", "d");
        } else if (typeDeclaration.type instanceof TStruct s) {
            if (visitedTypeNames.contains(s.name)) {
                return Map.of("t", "d");
            }
            final var nextVisited = new java.util.HashSet<>(visitedTypeNames);
            nextVisited.add(s.name);
            return Map.of(
                    "t", "s",
                    "f", s.fields.entrySet().stream()
                            .map(entry -> List.of(
                                    encodeMap.get(entry.getKey()),
                                    compileTypeDescriptor(entry.getValue().typeDeclaration, encodeMap, nextVisited)))
                            .toList());
        } else if (typeDeclaration.type instanceof TUnion u) {
            if (visitedTypeNames.contains(u.name)) {
                return Map.of("t", "d");
            }
            final var nextVisited = new java.util.HashSet<>(visitedTypeNames);
            nextVisited.add(u.name);
            return Map.of(
                    "t", "u",
                    "g", u.tags.entrySet().stream()
                            .map(entry -> List.of(
                                    encodeMap.get(entry.getKey()),
                                    Map.of(
                                            "t", "s",
                                            "f", entry.getValue().fields.entrySet().stream()
                                                    .map(fieldEntry -> List.of(
                                                            encodeMap.get(fieldEntry.getKey()),
                                                            compileTypeDescriptor(fieldEntry.getValue().typeDeclaration, encodeMap, nextVisited)))
                                                    .toList())))
                            .toList());
        }
        return Map.of("t", "v");
    }

    public static BinaryEncoding constructBinaryEncoding(TelepactSchema telepactSchema) {
        final var allKeys = new TreeSet<String>();
        final var requestPlanDescriptors = new ArrayList<Object>();
        final var responsePlanDescriptors = new ArrayList<Object>();

        final var sortedFunctionKeys = telepactSchema.parsed.keySet().stream()
                .filter(key -> key.startsWith("fn.") && telepactSchema.parsed.containsKey(key + ".->"))
                .sorted()
                .toList();

        for (final var entry : telepactSchema.parsed.entrySet()) {
            final var key = entry.getKey();
            final var value = entry.getValue();

            if (key.endsWith(".->") && value instanceof TUnion u) {
                final var result = u.tags.get("Ok_");
                allKeys.add("Ok_");
                for (final var fieldEntry : result.fields.entrySet()) {
                    final var fieldKey = fieldEntry.getKey();
                    final var field = fieldEntry.getValue();
                    allKeys.add(fieldKey);
                    final var keys = traceType(field.typeDeclaration);
                    keys.forEach(allKeys::add);
                }
            } else if (key.startsWith("fn.") && value instanceof TUnion u)  {
                allKeys.add(key);
                final var args = u.tags.get(key);
                for (final var fieldEntry : args.fields.entrySet()) {
                    final var fieldKey = fieldEntry.getKey();
                    final var field = fieldEntry.getValue();
                    allKeys.add(fieldKey);
                    final var keys = traceType(field.typeDeclaration);
                    keys.forEach(allKeys::add);
                }
            }

        }

        final var sortedAllKeys = new ArrayList<>(allKeys);
        Collections.sort(sortedAllKeys);

        final var binaryEncoding = new HashMap<String, Integer>();
        for (int index = 0; index < sortedAllKeys.size(); index++) {
            final var key = sortedAllKeys.get(index);
            binaryEncoding.put(key, index);
        }

        for (final var key : sortedFunctionKeys) {
            final var value = telepactSchema.parsed.get(key);
            if (!(key.startsWith("fn.")) || !(value instanceof TUnion u) || !telepactSchema.parsed.containsKey(key + ".->")) {
                continue;
            }
            requestPlanDescriptors.add(List.of(
                    binaryEncoding.get(key),
                    Map.of(
                            "t", "s",
                            "f", u.tags.get(key).fields.entrySet().stream()
                                    .map(fieldEntry -> List.of(
                                            binaryEncoding.get(fieldEntry.getKey()),
                                            compileTypeDescriptor(fieldEntry.getValue().typeDeclaration, binaryEncoding, java.util.Set.of())))
                                    .toList())));

            final var responseType = (TUnion) telepactSchema.parsed.get(key + ".->");
            responsePlanDescriptors.add(List.of(
                    binaryEncoding.get(key),
                    Map.of(
                            "t", "s",
                            "f", responseType.tags.get("Ok_").fields.entrySet().stream()
                                    .map(fieldEntry -> List.of(
                                            binaryEncoding.get(fieldEntry.getKey()),
                                            compileTypeDescriptor(fieldEntry.getValue().typeDeclaration, binaryEncoding, java.util.Set.of())))
                                    .toList())));
        }

        final var finalString = String.join("\n", sortedAllKeys);
        final var checksum = createChecksum(finalString);

        return new BinaryEncoding(binaryEncoding, checksum, sortedAllKeys, requestPlanDescriptors, responsePlanDescriptors);
    }
}
