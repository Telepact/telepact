package io.github.msgpact.internal;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import io.github.msgpact.internal.types.VArray;
import io.github.msgpact.internal.types.VFieldDeclaration;
import io.github.msgpact.internal.types.VFn;
import io.github.msgpact.internal.types.VObject;
import io.github.msgpact.internal.types.VStruct;
import io.github.msgpact.internal.types.VType;
import io.github.msgpact.internal.types.VTypeDeclaration;
import io.github.msgpact.internal.types.VUnion;

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
