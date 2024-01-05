package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class _SelectUtil {

    static Object selectStructFields(UTypeDeclaration typeDeclaration, Object value,
            Map<String, List<String>> selectedStructFields) {
        if (typeDeclaration.type instanceof UStruct s) {
            var selectedFields = selectedStructFields.get(s.name);
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
        } else if (typeDeclaration.type instanceof UFn f) {
            var valueAsMap = (Map<String, Object>) value;
            var unionEntry = UUnion.entry(valueAsMap);
            var unionValue = unionEntry.getKey();
            var unionData = (Map<String, Object>) unionEntry.getValue();

            var unionStructReference = f.call.values.get(unionValue);

            var selectedFields = selectedStructFields.get(unionStructReference.name);
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
        } else if (typeDeclaration.type instanceof UUnion e) {
            var valueAsMap = (Map<String, Object>) value;
            var unionEntry = UUnion.entry(valueAsMap);
            var unionValue = unionEntry.getKey();
            var unionData = (Map<String, Object>) unionEntry.getValue();

            var unionStructReference = e.values.get(unionValue);

            var selectedFields = selectedStructFields.get(unionStructReference.name);
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
        } else if (typeDeclaration.type instanceof UObject o) {
            var nestedTypeDeclaration = typeDeclaration.typeParameters.get(0);
            var valueAsMap = (Map<String, Object>) value;
            var finalMap = new HashMap<>();
            for (var entry : valueAsMap.entrySet()) {
                var valueWithSelectedFields = selectStructFields(nestedTypeDeclaration, entry.getValue(),
                        selectedStructFields);
                finalMap.put(entry.getKey(), valueWithSelectedFields);
            }
            return finalMap;
        } else if (typeDeclaration.type instanceof UArray a) {
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
