package uapi.internal;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import uapi.internal.types.UArray;
import uapi.internal.types.UFieldDeclaration;
import uapi.internal.types.UFn;
import uapi.internal.types.UObject;
import uapi.internal.types.UStruct;
import uapi.internal.types.UType;
import uapi.internal.types.UTypeDeclaration;
import uapi.internal.types.UUnion;

public class SelectStructFields {
    static Object selectStructFields(UTypeDeclaration typeDeclaration, Object value,
            Map<String, Object> selectedStructFields) {
        final UType typeDeclarationType = typeDeclaration.type;
        final List<UTypeDeclaration> typeDeclarationTypeParams = typeDeclaration.typeParameters;

        if (typeDeclarationType instanceof final UStruct s) {
            final Map<String, UFieldDeclaration> fields = s.fields;
            final String structName = s.name;
            final var selectedFields = (List<String>) selectedStructFields.get(structName);
            final var valueAsMap = (Map<String, Object>) value;
            final var finalMap = new HashMap<>();

            for (final var entry : valueAsMap.entrySet()) {
                final var fieldName = entry.getKey();
                if (selectedFields == null || selectedFields.contains(fieldName)) {
                    final var field = fields.get(fieldName);
                    final UTypeDeclaration fieldTypeDeclaration = field.typeDeclaration;
                    final var valueWithSelectedFields = selectStructFields(fieldTypeDeclaration, entry.getValue(),
                            selectedStructFields);

                    finalMap.put(entry.getKey(), valueWithSelectedFields);
                }
            }

            return finalMap;
        } else if (typeDeclarationType instanceof final UFn f) {
            final var valueAsMap = (Map<String, Object>) value;
            final Map.Entry<String, Object> uEntry = valueAsMap.entrySet().stream().findAny().get();
            final var unionTag = uEntry.getKey();
            final var unionData = (Map<String, Object>) uEntry.getValue();

            final String fnName = f.name;
            final UUnion fnCall = f.call;
            final Map<String, UStruct> fnCallTags = fnCall.tags;

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
        } else if (typeDeclarationType instanceof final UUnion u) {
            final var valueAsMap = (Map<String, Object>) value;
            final var uEntry = valueAsMap.entrySet().stream().findAny().get();
            final var unionTag = uEntry.getKey();
            final var unionData = (Map<String, Object>) uEntry.getValue();

            final Map<String, UStruct> unionTags = u.tags;
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
        } else if (typeDeclarationType instanceof final UObject o) {
            final var nestedTypeDeclaration = typeDeclarationTypeParams.get(0);
            final var valueAsMap = (Map<String, Object>) value;

            final var finalMap = new HashMap<>();
            for (final var entry : valueAsMap.entrySet()) {
                final var valueWithSelectedFields = selectStructFields(nestedTypeDeclaration, entry.getValue(),
                        selectedStructFields);
                finalMap.put(entry.getKey(), valueWithSelectedFields);
            }

            return finalMap;
        } else if (typeDeclarationType instanceof final UArray a) {
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
