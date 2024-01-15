package io.github.brenbar.uapi;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

class _SelectUtil {

    static Object selectStructFields(_UTypeDeclaration typeDeclaration, Object value,
            Map<String, Object> selectedStructFields) {
        final _UType typeDeclarationType = typeDeclaration.type;
        final List<_UTypeDeclaration> typeDeclarationTypeParams = typeDeclaration.typeParameters;

        if (typeDeclarationType instanceof final _UStruct s) {
            final Map<String, _UFieldDeclaration> fields = s.fields;
            final String structName = s.name;
            final var selectedFields = (List<String>) selectedStructFields.get(structName);
            final var valueAsMap = (Map<String, Object>) value;
            final var finalMap = new HashMap<>();

            for (final var entry : valueAsMap.entrySet()) {
                final var fieldName = entry.getKey();
                if (selectedFields == null || selectedFields.contains(fieldName)) {
                    final var field = fields.get(fieldName);
                    final _UTypeDeclaration fieldTypeDeclaration = field.typeDeclaration;
                    final var valueWithSelectedFields = selectStructFields(fieldTypeDeclaration, entry.getValue(),
                            selectedStructFields);

                    finalMap.put(entry.getKey(), valueWithSelectedFields);
                }
            }

            return finalMap;
        } else if (typeDeclarationType instanceof final _UFn f) {
            final var valueAsMap = (Map<String, Object>) value;
            final Map.Entry<String, Object> unionEntry = _UUnion.entry(valueAsMap);
            final var unionCase = unionEntry.getKey();
            final var unionData = (Map<String, Object>) unionEntry.getValue();

            final String fnName = f.name;
            final _UUnion fnCall = f.call;
            final Map<String, _UStruct> fnCallCases = fnCall.cases;

            final var argStructReference = fnCallCases.get(unionCase);
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

            return Map.of(unionEntry.getKey(), finalMap);
        } else if (typeDeclarationType instanceof final _UUnion u) {
            final var valueAsMap = (Map<String, Object>) value;
            final var unionEntry = _UUnion.entry(valueAsMap);
            final var unionCase = unionEntry.getKey();
            final var unionData = (Map<String, Object>) unionEntry.getValue();

            final Map<String, _UStruct> unionCases = u.cases;
            final var unionStructReference = unionCases.get(unionCase);
            final var unionStructRefFields = unionStructReference.fields;
            final var defaultCasesToFields = new HashMap<String, List<String>>();

            for (final var entry : unionCases.entrySet()) {
                final var unionStruct = entry.getValue();
                final var unionStructFields = unionStruct.fields;
                final var fields = unionStructFields.keySet().stream().toList();
                defaultCasesToFields.put(entry.getKey(), fields);
            }

            final var unionSelectedFields = (Map<String, Object>) selectedStructFields.getOrDefault(u.name,
                    defaultCasesToFields);
            final var thisUnionCaseSelectedFieldsDefault = defaultCasesToFields.get(unionCase);
            final var selectedFields = (List<String>) unionSelectedFields.getOrDefault(unionCase,
                    thisUnionCaseSelectedFieldsDefault);

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

            return Map.of(unionEntry.getKey(), finalMap);
        } else if (typeDeclarationType instanceof final _UObject o) {
            final var nestedTypeDeclaration = typeDeclarationTypeParams.get(0);
            final var valueAsMap = (Map<String, Object>) value;

            final var finalMap = new HashMap<>();
            for (final var entry : valueAsMap.entrySet()) {
                final var valueWithSelectedFields = selectStructFields(nestedTypeDeclaration, entry.getValue(),
                        selectedStructFields);
                finalMap.put(entry.getKey(), valueWithSelectedFields);
            }

            return finalMap;
        } else if (typeDeclarationType instanceof final _UArray a) {
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
