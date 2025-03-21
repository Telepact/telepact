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

package io.github.telepact.internal;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import io.github.telepact.internal.types.VArray;
import io.github.telepact.internal.types.VFieldDeclaration;
import io.github.telepact.internal.types.VFn;
import io.github.telepact.internal.types.VObject;
import io.github.telepact.internal.types.VStruct;
import io.github.telepact.internal.types.VType;
import io.github.telepact.internal.types.VTypeDeclaration;
import io.github.telepact.internal.types.VUnion;

public class SelectStructFields {
    static Object selectStructFields(VTypeDeclaration typeDeclaration, Object value,
            Map<String, Object> selectedStructFields) {
        final VType typeDeclarationType = typeDeclaration.type;
        final List<VTypeDeclaration> typeDeclarationTypeParams = typeDeclaration.typeParameters;

        if (typeDeclarationType instanceof final VStruct s) {
            final Map<String, VFieldDeclaration> fields = s.fields;
            final String structName = s.name;
            final var selectedFields = (List<String>) selectedStructFields.get(structName);
            final var valueAsMap = (Map<String, Object>) value;
            final var finalMap = new HashMap<>();

            for (final var entry : valueAsMap.entrySet()) {
                final var fieldName = entry.getKey();
                if (selectedFields == null || selectedFields.contains(fieldName)) {
                    final var field = fields.get(fieldName);
                    final VTypeDeclaration fieldTypeDeclaration = field.typeDeclaration;
                    final var valueWithSelectedFields = selectStructFields(fieldTypeDeclaration, entry.getValue(),
                            selectedStructFields);

                    finalMap.put(entry.getKey(), valueWithSelectedFields);
                }
            }

            return finalMap;
        } else if (typeDeclarationType instanceof final VFn f) {
            final var valueAsMap = (Map<String, Object>) value;
            final Map.Entry<String, Object> uEntry = valueAsMap.entrySet().stream().findAny().get();
            final var unionTag = uEntry.getKey();
            final var unionData = (Map<String, Object>) uEntry.getValue();

            final String fnName = f.name;
            final VUnion fnCall = f.call;
            final Map<String, VStruct> fnCallTags = fnCall.tags;

            final var argStructReference = fnCallTags.get(unionTag);
            final var selectedFields = (List<String>) selectedStructFields.get(fnName);
            final var finalMap = new HashMap<>();

            for (final var entry : unionData.entrySet()) {
                final var fieldName = entry.getKey();
                if (selectedFields == null || selectedFields.contains(fieldName)) {
                    final var field = argStructReference.fields.get(fieldName);
                    final var valueWithSelectedFields = selectStructFields(field.typeDeclaration, entry.getValue(),
                            selectedStructFields);

                    finalMap.put(entry.getKey(), valueWithSelectedFields);
                }
            }

            return Map.of(uEntry.getKey(), finalMap);
        } else if (typeDeclarationType instanceof final VUnion u) {
            final var valueAsMap = (Map<String, Object>) value;
            final var uEntry = valueAsMap.entrySet().stream().findAny().get();
            final var unionTag = uEntry.getKey();
            final var unionData = (Map<String, Object>) uEntry.getValue();

            final Map<String, VStruct> unionTags = u.tags;
            final var unionStructReference = unionTags.get(unionTag);
            final var unionStructRefFields = unionStructReference.fields;
            final var defaultTagsToFields = new HashMap<String, List<String>>();

            for (final var entry : unionTags.entrySet()) {
                final var unionStruct = entry.getValue();
                final var unionStructFields = unionStruct.fields;
                final var fieldNames = unionStructFields.keySet().stream().toList();
                defaultTagsToFields.put(entry.getKey(), fieldNames);
            }

            final var unionSelectedFields = (Map<String, Object>) selectedStructFields.getOrDefault(u.name,
                    defaultTagsToFields);
            final var thisUnionTagSelectedFieldsDefault = defaultTagsToFields.get(unionTag);
            final var selectedFields = (List<String>) unionSelectedFields.getOrDefault(unionTag,
                    thisUnionTagSelectedFieldsDefault);

            final var finalMap = new HashMap<>();
            for (final var entry : unionData.entrySet()) {
                final var fieldName = entry.getKey();
                if (selectedFields == null || selectedFields.contains(fieldName)) {
                    final var field = unionStructRefFields.get(fieldName);
                    final var valueWithSelectedFields = selectStructFields(field.typeDeclaration, entry.getValue(),
                            selectedStructFields);
                    finalMap.put(entry.getKey(), valueWithSelectedFields);
                }
            }

            return Map.of(uEntry.getKey(), finalMap);
        } else if (typeDeclarationType instanceof final VObject o) {
            final var nestedTypeDeclaration = typeDeclarationTypeParams.get(0);
            final var valueAsMap = (Map<String, Object>) value;

            final var finalMap = new HashMap<>();
            for (final var entry : valueAsMap.entrySet()) {
                final var valueWithSelectedFields = selectStructFields(nestedTypeDeclaration, entry.getValue(),
                        selectedStructFields);
                finalMap.put(entry.getKey(), valueWithSelectedFields);
            }

            return finalMap;
        } else if (typeDeclarationType instanceof final VArray a) {
            final var nestedType = typeDeclarationTypeParams.get(0);
            final var valueAsList = (List<Object>) value;

            final var finalList = new ArrayList<>();
            for (final var entry : valueAsList) {
                final var valueWithSelectedFields = selectStructFields(nestedType, entry, selectedStructFields);
                finalList.add(valueWithSelectedFields);
            }

            return finalList;
        } else {
            return value;
        }
    }
}
