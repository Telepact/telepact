package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

class _SelectUtil {

    static Object selectStructFields(_UTypeDeclaration typeDeclaration, Object value,
            Map<String, Object> selectedStructFields) {
        if (typeDeclaration.type instanceof _UStruct s) {
            var selectedFields = (List<String>) selectedStructFields.get(s.name);
            var valueAsMap = (Map<String, Object>) value;
            var finalMap = new HashMap<>();
            for (var entry : valueAsMap.entrySet()) {
                var fieldName = entry.getKey();
                if (selectedFields == null || selectedFields.contains(fieldName)) {
                    var field = s.fields.get(fieldName);
                    var valueWithSelectedFields = selectStructFields(field.typeDeclaration, entry.getValue(),
                            selectedStructFields);
                    finalMap.put(entry.getKey(), valueWithSelectedFields);
                }
            }
            return finalMap;
        } else if (typeDeclaration.type instanceof _UFn f) {
            var valueAsMap = (Map<String, Object>) value;
            var unionEntry = _UUnion.entry(valueAsMap);
            var unionCase = unionEntry.getKey();
            var unionData = (Map<String, Object>) unionEntry.getValue();

            var argStructReference = f.call.cases.get(unionCase);

            var selectedFields = (List<String>) selectedStructFields.get(f.name);
            var finalMap = new HashMap<>();
            for (var entry : unionData.entrySet()) {
                var fieldName = entry.getKey();
                if (selectedFields == null || selectedFields.contains(fieldName)) {
                    var field = argStructReference.fields.get(fieldName);
                    var valueWithSelectedFields = selectStructFields(field.typeDeclaration, entry.getValue(),
                            selectedStructFields);
                    finalMap.put(entry.getKey(), valueWithSelectedFields);
                }
            }

            return Map.of(unionEntry.getKey(), finalMap);
        } else if (typeDeclaration.type instanceof _UUnion u) {
            var valueAsMap = (Map<String, Object>) value;
            var unionEntry = _UUnion.entry(valueAsMap);
            var unionCase = unionEntry.getKey();
            var unionData = (Map<String, Object>) unionEntry.getValue();

            var unionStructReference = u.cases.get(unionCase);

            var defaultCasesToFields = new HashMap<String, List<String>>();
            for (var entry : u.cases.entrySet()) {
                var fields = entry.getValue().fields.keySet().stream().toList();
                defaultCasesToFields.put(entry.getKey(), fields);
            }

            var unionSelectedFields = (Map<String, Object>) selectedStructFields.getOrDefault(u.name,
                    defaultCasesToFields);
            var thisUnionCaseSelectedFieldsDefault = defaultCasesToFields.get(unionCase);
            var selectedFields = (List<String>) unionSelectedFields.getOrDefault(unionCase,
                    thisUnionCaseSelectedFieldsDefault);

            var finalMap = new HashMap<>();
            for (var entry : unionData.entrySet()) {
                var fieldName = entry.getKey();
                if (selectedFields == null || selectedFields.contains(fieldName)) {
                    var field = unionStructReference.fields.get(fieldName);
                    var valueWithSelectedFields = selectStructFields(field.typeDeclaration, entry.getValue(),
                            selectedStructFields);
                    finalMap.put(entry.getKey(), valueWithSelectedFields);
                }
            }

            return Map.of(unionEntry.getKey(), finalMap);
        } else if (typeDeclaration.type instanceof _UObject o) {
            var nestedTypeDeclaration = typeDeclaration.typeParameters.get(0);
            var valueAsMap = (Map<String, Object>) value;
            var finalMap = new HashMap<>();
            for (var entry : valueAsMap.entrySet()) {
                var valueWithSelectedFields = selectStructFields(nestedTypeDeclaration, entry.getValue(),
                        selectedStructFields);
                finalMap.put(entry.getKey(), valueWithSelectedFields);
            }
            return finalMap;
        } else if (typeDeclaration.type instanceof _UArray a) {
            var nestedType = typeDeclaration.typeParameters.get(0);
            var valueAsList = (List<Object>) value;
            var finalList = new ArrayList<>();
            for (var entry : valueAsList) {
                var valueWithSelectedFields = selectStructFields(nestedType, entry, selectedStructFields);
                finalList.add(valueWithSelectedFields);
            }
            return finalList;
        } else {
            return value;
        }
    }

}
