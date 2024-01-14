package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

public class _UStruct implements _UType {

    public final String name;
    public final Map<String, _UFieldDeclaration> fields;
    public final int typeParameterCount;

    public _UStruct(String name, Map<String, _UFieldDeclaration> fields, int typeParameterCount) {
        this.name = name;
        this.fields = fields;
        this.typeParameterCount = typeParameterCount;
    }

    @Override
    public int getTypeParameterCount() {
        return this.typeParameterCount;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        if (value instanceof Map<?, ?> m) {
            return validateStructFields(this.fields, (Map<String, Object>) m, typeParameters);
        } else {
            return _ValidateUtil.getTypeUnexpectedValidationFailure(List.of(), value,
                    this.getName(generics));
        }
    }

    public static List<ValidationFailure> validateStructFields(
            Map<String, _UFieldDeclaration> fields,
            Map<String, Object> actualStruct, List<_UTypeDeclaration> typeParameters) {
        var validationFailures = new ArrayList<ValidationFailure>();

        var missingFields = new ArrayList<String>();
        for (Map.Entry<String, _UFieldDeclaration> entry : fields.entrySet()) {
            var fieldName = entry.getKey();
            var fieldDeclaration = entry.getValue();
            if (!actualStruct.containsKey(fieldName) && !fieldDeclaration.optional) {
                missingFields.add(fieldName);
            }
        }

        for (var missingField : missingFields) {
            var validationFailure = new ValidationFailure(List.of(missingField),
                    "RequiredStructFieldMissing", Map.of());
            validationFailures
                    .add(validationFailure);
        }

        for (Map.Entry<String, Object> entry : actualStruct.entrySet()) {
            var fieldName = entry.getKey();
            var fieldValue = entry.getValue();
            var referenceField = fields.get(fieldName);
            if (referenceField == null) {
                var validationFailure = new ValidationFailure(List.of(fieldName),
                        "StructFieldUnknown", Map.of());
                validationFailures
                        .add(validationFailure);
                continue;
            }
            var nestedValidationFailures = referenceField.typeDeclaration.validate(fieldValue, typeParameters);
            var nestedValidationFailuresWithPath = nestedValidationFailures
                    .stream()
                    .map(f -> new ValidationFailure(_ValidateUtil.prepend(fieldName, f.path), f.reason,
                            f.data))
                    .toList();
            validationFailures.addAll(nestedValidationFailuresWithPath);
        }

        return validationFailures;
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            RandomGenerator random) {
        if (useStartingValue) {
            var startingStructValue = (Map<String, Object>) startingValue;
            return constructRandomStruct(this.fields, startingStructValue, includeRandomOptionalFields,
                    typeParameters, random);
        } else {
            return constructRandomStruct(this.fields, new HashMap<>(), includeRandomOptionalFields,
                    typeParameters, random);
        }
    }

    public static Map<String, Object> constructRandomStruct(
            Map<String, _UFieldDeclaration> referenceStruct, Map<String, Object> startingStruct,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            RandomGenerator random) {

        var sortedReferenceStruct = new ArrayList<>(referenceStruct.entrySet());
        Collections.sort(sortedReferenceStruct, (e1, e2) -> e1.getKey().compareTo(e2.getKey()));

        var obj = new TreeMap<String, Object>();
        for (var field : sortedReferenceStruct) {
            var fieldName = field.getKey();
            var fieldDeclaration = field.getValue();
            var startingValue = startingStruct.get(fieldName);
            var useStartingValue = startingStruct.containsKey(fieldName);
            Object value;
            if (useStartingValue) {
                value = fieldDeclaration.typeDeclaration.generateRandomValue(startingValue, useStartingValue,
                        includeRandomOptionalFields, typeParameters,
                        random);
            } else {
                if (!fieldDeclaration.optional) {
                    value = fieldDeclaration.typeDeclaration.generateRandomValue(null, false,
                            includeRandomOptionalFields, typeParameters, random);
                } else {
                    if (!includeRandomOptionalFields) {
                        continue;
                    }
                    if (random.nextBoolean()) {
                        continue;
                    }
                    value = fieldDeclaration.typeDeclaration.generateRandomValue(null, false,
                            includeRandomOptionalFields, typeParameters, random);
                }
            }
            obj.put(fieldName, value);
        }
        return obj;
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        return "Object";
    }
}
