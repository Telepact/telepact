package io.github.brenbar.japi;

import java.util.Map;

class ValidateEnum {

    static void validateEnum(
            String namespace,
            Map<String, Struct> reference,
            String enumCase,
            Map<String, Object> actual) {
        var referenceField = reference.get(enumCase);
        if (referenceField == null) {
            throw new Error.UnknownEnumField(namespace, enumCase);
        }

        ValidateStruct.validate("%s.%s".formatted(namespace, enumCase), referenceField.fields(), actual);
    }
}
