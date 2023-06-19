package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

class ValidateStruct {

    static void validate(
            String namespace,
            Map<String, FieldDeclaration> referenceStruct,
            Map<String, Object> actualStruct) {
        var missingFields = new ArrayList<String>();
        for (Map.Entry<String, FieldDeclaration> entry : referenceStruct.entrySet()) {
            var fieldName = entry.getKey();
            var fieldDeclaration = entry.getValue();
            if (!actualStruct.containsKey(fieldName) && !fieldDeclaration.optional()) {
                missingFields.add(fieldName);
            }
        }

        if (!missingFields.isEmpty()) {
            throw new Error.StructMissingFields(namespace, missingFields);
        }

        var extraFields = new ArrayList<String>();
        for (Map.Entry<String, Object> entry : actualStruct.entrySet()) {
            var name = entry.getKey();
            if (!referenceStruct.containsKey(name)) {
                extraFields.add(name);
            }
        }

        if (!extraFields.isEmpty()) {
            throw new Error.StructHasExtraFields(namespace, extraFields);
        }

        for (Map.Entry<String, Object> entry : actualStruct.entrySet()) {
            var fieldName = entry.getKey();
            var field = entry.getValue();
            var referenceField = referenceStruct.get(fieldName);
            if (referenceField == null) {
                throw new Error.StructHasExtraFields(namespace, List.of(fieldName));
            }
            ValidateType.validateType("%s.%s".formatted(namespace, fieldName), referenceField.typeDeclaration(), field);
        }
    }
}
