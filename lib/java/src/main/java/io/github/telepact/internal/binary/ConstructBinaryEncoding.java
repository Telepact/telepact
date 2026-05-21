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
import io.github.telepact.internal.types.TAny;
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
        } else if (typeDeclaration.type instanceof TAny) {
            return thisAllKeys;
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

    private static List<Object> buildPackHeader(TTypeDeclaration typeDeclaration, Object rootKey) {
        final var header = new ArrayList<Object>();
        header.add(rootKey);
        if (!(typeDeclaration.type instanceof TStruct s)) {
            return header;
        }
        final var sortedFieldKeys = new TreeSet<>(s.fields.keySet());
        for (final var fieldKey : sortedFieldKeys) {
            final var field = s.fields.get(fieldKey);
            if (field.typeDeclaration.type instanceof TStruct) {
                header.add(buildPackHeader(field.typeDeclaration, fieldKey));
            } else {
                header.add(fieldKey);
            }
        }
        return header;
    }

    private static List<Object> collectPackSites(
            TTypeDeclaration typeDeclaration,
            List<String> path,
            List<Object> packSites,
            Map<String, Boolean> activeTypeNames,
            boolean underGenericList) {
        if (typeDeclaration.type instanceof TArray) {
            if (typeDeclaration.typeParameters.isEmpty()) {
                return packSites;
            }
            final var itemType = typeDeclaration.typeParameters.get(0);
            if (!underGenericList && itemType.type instanceof TStruct) {
                packSites.add(List.of(new ArrayList<>(path), buildPackHeader(itemType, null)));
                return packSites;
            }
            return collectPackSites(itemType, path, packSites, activeTypeNames, true);
        }
        if (typeDeclaration.type instanceof TAny || typeDeclaration.type instanceof TObject) {
            return packSites;
        }
        if (typeDeclaration.type instanceof TStruct s) {
            if (activeTypeNames.containsKey(s.name)) {
                return packSites;
            }
            final var nextActive = new HashMap<>(activeTypeNames);
            nextActive.put(s.name, true);
            final var sortedFieldKeys = new TreeSet<>(s.fields.keySet());
            for (final var fieldKey : sortedFieldKeys) {
                final var nextPath = new ArrayList<>(path);
                nextPath.add(fieldKey);
                collectPackSites(s.fields.get(fieldKey).typeDeclaration, nextPath, packSites, nextActive, underGenericList);
            }
            return packSites;
        }
        if (typeDeclaration.type instanceof TUnion u) {
            if (activeTypeNames.containsKey(u.name)) {
                return packSites;
            }
            final var nextActive = new HashMap<>(activeTypeNames);
            nextActive.put(u.name, true);
            final var sortedTagKeys = new TreeSet<>(u.tags.keySet());
            for (final var tagKey : sortedTagKeys) {
                final var tagStruct = u.tags.get(tagKey);
                final var sortedFieldKeys = new TreeSet<>(tagStruct.fields.keySet());
                for (final var fieldKey : sortedFieldKeys) {
                    final var nextPath = new ArrayList<>(path);
                    nextPath.add(tagKey);
                    nextPath.add(fieldKey);
                    collectPackSites(tagStruct.fields.get(fieldKey).typeDeclaration, nextPath, packSites, nextActive, underGenericList);
                }
            }
        }
        return packSites;
    }

    public static BinaryEncoding constructBinaryEncoding(TelepactSchema telepactSchema) {
        final var allKeys = new TreeSet<String>();
        final var packSites = new ArrayList<Object>();

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
                    collectPackSites(field.typeDeclaration, new ArrayList<>(List.of("Ok_", fieldKey)), packSites, new HashMap<>(), false);
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
                    collectPackSites(field.typeDeclaration, new ArrayList<>(List.of(key, fieldKey)), packSites, new HashMap<>(), false);
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

        final var finalString = String.join("\n", sortedAllKeys);
        final var checksum = createChecksum(finalString);

        return new BinaryEncoding(binaryEncoding, checksum, packSites);
    }
}