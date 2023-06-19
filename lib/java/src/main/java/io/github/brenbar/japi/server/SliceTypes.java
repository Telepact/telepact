package io.github.brenbar.japi.server;

import io.github.brenbar.japi.Parser;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

class SliceTypes {
    static Object sliceTypes(Parser.Type type, Object value, Map<String, List<String>> slicedTypes) {
        if (type instanceof Parser.Struct s) {
            var slicedFields = slicedTypes.get(s.name());
            var valueAsMap = (Map<String, Object>) value;
            var finalMap = new HashMap<>();
            for (var entry : valueAsMap.entrySet()) {
                if (slicedFields == null || slicedFields.contains(entry.getKey())) {
                    var field = s.fields().get(entry.getKey());
                    var slicedValue = sliceTypes(field.typeDeclaration().type(), entry.getValue(), slicedTypes);
                    finalMap.put(entry.getKey(), slicedValue);
                }
            }
            return finalMap;
        } else if (type instanceof Parser.Enum e) {
            var valueAsMap = (Map<String, Object>) value;
            var enumEntry = valueAsMap.entrySet().stream().findFirst().get();
            var structReference = e.cases().get(enumEntry.getKey());
            Map<String, Object> newStruct = new HashMap<>();
            for (var structEntry : structReference.fields().entrySet()) {
                var slicedValue = sliceTypes(structEntry.getValue().typeDeclaration().type(), enumEntry.getValue(), slicedTypes);
                newStruct.put(structEntry.getKey(), slicedValue);
            }
            return Map.of(enumEntry.getKey(), newStruct);
        } else if (type instanceof Parser.JsonObject o) {
            var valueAsMap = (Map<String, Object>) value;
            var finalMap = new HashMap<>();
            for (var entry : valueAsMap.entrySet()) {
                var slicedValue = sliceTypes(o.nestedType().type(), entry.getValue(), slicedTypes);
                finalMap.put(entry.getKey(), slicedValue);
            }
            return finalMap;
        } else if (type instanceof Parser.JsonArray a) {
            var valueAsList = (List<Object>) value;
            var finalList = new ArrayList<>();
            for (var entry : valueAsList) {
                var slicedValue = sliceTypes(a.nestedType().type(), entry, slicedTypes);
                finalList.add(slicedValue);
            }
            return finalList;
        } else {
            return value;
        }
    }
}
