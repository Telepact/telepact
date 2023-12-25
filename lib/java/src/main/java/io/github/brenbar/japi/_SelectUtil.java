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
            var selectedFields = selectedStructFields.get(f.name);
            var valueAsMap = (Map<String, Object>) value;
            var finalMap = new HashMap<>();
            for (var entry : valueAsMap.entrySet()) {
                var fieldName = entry.getKey();
                if (selectedFields == null || selectedFields.contains(fieldName)) {
                    var field = f.arg.fields.get(fieldName);
                    var valueWithSelectedFields = selectStructFields(field.typeDeclaration, entry.getValue(),
                            selectedStructFields);
                    finalMap.put(entry.getKey(), valueWithSelectedFields);
                }
            }
            return finalMap;
        } else if (typeDeclaration.type instanceof UEnum e) {
            var valueAsMap = (Map<String, Object>) value;
            var enumEntry = valueAsMap.entrySet().stream().findFirst().get();
            var enumValue = enumEntry.getKey();
            var enumData = (Map<String, Object>) enumEntry.getValue();

            var enumStructReference = e.values.get(enumValue);

            var selectedFields = selectedStructFields.get(enumStructReference.name);
            var finalMap = new HashMap<>();
            for (var entry : enumData.entrySet()) {
                var fieldName = entry.getKey();
                if (selectedFields == null || selectedFields.contains(fieldName)) {
                    var field = enumStructReference.fields.get(fieldName);
                    var valueWithSelectedFields = selectStructFields(field.typeDeclaration, entry.getValue(),
                            selectedStructFields);
                    finalMap.put(entry.getKey(), valueWithSelectedFields);
                }
            }

            return Map.of(enumEntry.getKey(), finalMap);
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
