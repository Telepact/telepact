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
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeSet;

import io.github.telepact.TelepactSchema;
import io.github.telepact.internal.types.TArray;
import io.github.telepact.internal.types.TFieldDeclaration;
import io.github.telepact.internal.types.TObject;
import io.github.telepact.internal.types.TStruct;
import io.github.telepact.internal.types.TTypeDeclaration;
import io.github.telepact.internal.types.TUnion;

public class ConstructBinaryEncoding {

    private static List<String> traceType(TTypeDeclaration typeDeclaration, Set<String> visitedTypeNames) {
        final var thisAllKeys = new ArrayList<String>();

        if (typeDeclaration.type instanceof TArray) {
            thisAllKeys.addAll(traceType(typeDeclaration.typeParameters.get(0), visitedTypeNames));
        } else if (typeDeclaration.type instanceof TObject) {
            thisAllKeys.addAll(traceType(typeDeclaration.typeParameters.get(0), visitedTypeNames));
        } else if (typeDeclaration.type instanceof TStruct s) {
            if (visitedTypeNames.contains(s.name)) {
                return thisAllKeys;
            }
            final var nextVisitedTypeNames = new HashSet<>(visitedTypeNames);
            nextVisitedTypeNames.add(s.name);
            for (final var entry : s.fields.entrySet()) {
                thisAllKeys.add(entry.getKey());
                thisAllKeys.addAll(traceType(entry.getValue().typeDeclaration, nextVisitedTypeNames));
            }
        } else if (typeDeclaration.type instanceof TUnion u) {
            if (visitedTypeNames.contains(u.name)) {
                return thisAllKeys;
            }
            final var nextVisitedTypeNames = new HashSet<>(visitedTypeNames);
            nextVisitedTypeNames.add(u.name);
            for (final var entry : u.tags.entrySet()) {
                thisAllKeys.add(entry.getKey());
                for (final var fieldEntry : entry.getValue().fields.entrySet()) {
                    thisAllKeys.add(fieldEntry.getKey());
                    thisAllKeys.addAll(traceType(fieldEntry.getValue().typeDeclaration, nextVisitedTypeNames));
                }
            }
        }

        return thisAllKeys;
    }

    private static boolean isDeterministicPackedStruct(TTypeDeclaration typeDeclaration, Set<String> visitingTypeNames) {
        if (typeDeclaration.type instanceof TArray) {
            final var childType = typeDeclaration.typeParameters.get(0);
            return !(childType.type instanceof TStruct || childType.type instanceof TUnion);
        }

        if (typeDeclaration.type instanceof TObject) {
            return true;
        }

        if (typeDeclaration.type instanceof TStruct s) {
            if (visitingTypeNames.contains(s.name)) {
                return false;
            }
            final var nextVisitingTypeNames = new HashSet<>(visitingTypeNames);
            nextVisitingTypeNames.add(s.name);
            for (final var field : s.fields.values()) {
                if (!isDeterministicPackedStruct(field.typeDeclaration, nextVisitingTypeNames)) {
                    return false;
                }
            }
            return true;
        }

        if (typeDeclaration.type instanceof TUnion u) {
            if (visitingTypeNames.contains(u.name)) {
                return false;
            }
            final var nextVisitingTypeNames = new HashSet<>(visitingTypeNames);
            nextVisitingTypeNames.add(u.name);
            for (final var tagValue : u.tags.values()) {
                for (final var field : tagValue.fields.values()) {
                    if (!isDeterministicPackedStruct(field.typeDeclaration, nextVisitingTypeNames)) {
                        return false;
                    }
                }
            }
            return true;
        }

        return true;
    }

    private static Integer getEncodedKey(Map<String, Integer> binaryEncoding, String key) {
        final var encodedKey = binaryEncoding.get(key);
        if (encodedKey == null) {
            throw new IllegalArgumentException("Missing binary encoding for key " + key);
        }
        return encodedKey;
    }

    private static Object buildNestedHeader(String key, TTypeDeclaration typeDeclaration, Map<String, Integer> binaryEncoding) {
        final var encodedKey = getEncodedKey(binaryEncoding, key);

        if (typeDeclaration.type instanceof TStruct s) {
            final var header = new ArrayList<Object>();
            header.add(encodedKey);
            for (final var entry : s.fields.entrySet()) {
                header.add(buildNestedHeader(entry.getKey(), entry.getValue().typeDeclaration, binaryEncoding));
            }
            return header;
        }

        if (typeDeclaration.type instanceof TUnion u) {
            final var header = new ArrayList<Object>();
            header.add(encodedKey);
            for (final var entry : u.tags.entrySet()) {
                final var tagHeader = new ArrayList<Object>();
                tagHeader.add(getEncodedKey(binaryEncoding, entry.getKey()));
                for (final var fieldEntry : entry.getValue().fields.entrySet()) {
                    tagHeader.add(buildNestedHeader(fieldEntry.getKey(), fieldEntry.getValue().typeDeclaration, binaryEncoding));
                }
                header.add(tagHeader);
            }
            return header;
        }

        return encodedKey;
    }

    private static List<Object> buildPackHeader(TStruct structType, Map<String, Integer> binaryEncoding) {
        final var header = new ArrayList<Object>();
        header.add(null);
        for (final var entry : structType.fields.entrySet()) {
            header.add(buildNestedHeader(entry.getKey(), entry.getValue().typeDeclaration, binaryEncoding));
        }
        return header;
    }

    private static void collectPackedSites(List<String> path, TTypeDeclaration typeDeclaration,
            Map<String, Integer> binaryEncoding, List<List<Object>> packedSites, Set<String> visitedTypeNames) {
        if (typeDeclaration.type instanceof TArray) {
            final var childType = typeDeclaration.typeParameters.get(0);
            if (childType.type instanceof final TStruct s && isDeterministicPackedStruct(childType, new HashSet<>())) {
                packedSites.add(new ArrayList<>(List.of(new ArrayList<>(path), buildPackHeader(s, binaryEncoding))));
            }
            return;
        }

        if (typeDeclaration.type instanceof TObject) {
            return;
        }

        if (typeDeclaration.type instanceof TStruct s) {
            if (visitedTypeNames.contains(s.name)) {
                return;
            }
            final var nextVisitedTypeNames = new HashSet<>(visitedTypeNames);
            nextVisitedTypeNames.add(s.name);
            for (final var entry : s.fields.entrySet()) {
                final var nextPath = new ArrayList<>(path);
                nextPath.add(entry.getKey());
                collectPackedSites(nextPath, entry.getValue().typeDeclaration, binaryEncoding, packedSites, nextVisitedTypeNames);
            }
            return;
        }

        if (typeDeclaration.type instanceof TUnion u) {
            if (visitedTypeNames.contains(u.name)) {
                return;
            }
            final var nextVisitedTypeNames = new HashSet<>(visitedTypeNames);
            nextVisitedTypeNames.add(u.name);
            for (final var entry : u.tags.entrySet()) {
                for (final var fieldEntry : entry.getValue().fields.entrySet()) {
                    final var nextPath = new ArrayList<>(path);
                    nextPath.add(entry.getKey());
                    nextPath.add(fieldEntry.getKey());
                    collectPackedSites(nextPath, fieldEntry.getValue().typeDeclaration, binaryEncoding, packedSites, nextVisitedTypeNames);
                }
            }
        }
    }

    private static void addRootPackedSites(List<String> rootPath, Map<String, TFieldDeclaration> fields,
            Map<String, Integer> binaryEncoding, List<List<Object>> packedSites) {
        for (final var entry : fields.entrySet()) {
            final var nextPath = new ArrayList<>(rootPath);
            nextPath.add(entry.getKey());
            collectPackedSites(nextPath, entry.getValue().typeDeclaration, binaryEncoding, packedSites, new HashSet<>());
        }
    }

    public static BinaryEncoding constructBinaryEncoding(TelepactSchema telepactSchema) {
        final var allKeys = new TreeSet<String>();

        for (final var entry : telepactSchema.parsed.entrySet()) {
            final var key = entry.getKey();
            final var value = entry.getValue();

            if (key.endsWith(".->") && value instanceof TUnion u) {
                final var result = u.tags.get("Ok_");
                if (result == null) {
                    continue;
                }
                allKeys.add("Ok_");
                for (final var fieldEntry : result.fields.entrySet()) {
                    allKeys.add(fieldEntry.getKey());
                    traceType(fieldEntry.getValue().typeDeclaration, new HashSet<>()).forEach(allKeys::add);
                }
            } else if (key.startsWith("fn.") && value instanceof TUnion u)  {
                allKeys.add(key);
                final var args = u.tags.get(key);
                if (args == null) {
                    continue;
                }
                for (final var fieldEntry : args.fields.entrySet()) {
                    allKeys.add(fieldEntry.getKey());
                    traceType(fieldEntry.getValue().typeDeclaration, new HashSet<>()).forEach(allKeys::add);
                }
            }
        }

        final var sortedAllKeys = new ArrayList<>(allKeys);
        Collections.sort(sortedAllKeys);

        final var binaryEncoding = new HashMap<String, Integer>();
        for (int index = 0; index < sortedAllKeys.size(); index++) {
            binaryEncoding.put(sortedAllKeys.get(index), index);
        }

        final var packedSites = new ArrayList<List<Object>>();
        for (final var entry : telepactSchema.parsed.entrySet()) {
            final var key = entry.getKey();
            final var value = entry.getValue();

            if (key.endsWith(".->") && value instanceof TUnion u) {
                final var result = u.tags.get("Ok_");
                if (result != null) {
                    addRootPackedSites(new ArrayList<>(List.of("Ok_")), result.fields, binaryEncoding, packedSites);
                }
            } else if (key.startsWith("fn.") && value instanceof TUnion u) {
                final var args = u.tags.get(key);
                if (args != null) {
                    addRootPackedSites(new ArrayList<>(List.of(key)), args.fields, binaryEncoding, packedSites);
                }
            }
        }

        final var finalString = String.join("\n", sortedAllKeys);
        final var checksum = createChecksum(finalString);

        return new BinaryEncoding(binaryEncoding, checksum, packedSites);
    }
}
