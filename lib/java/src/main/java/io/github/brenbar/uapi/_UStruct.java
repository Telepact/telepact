package io.github.brenbar.uapi;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

class _UStruct implements _UType {

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
    public List<_ValidationFailure> validate(Object value, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        if (value instanceof Map<?, ?> m) {
            return validateStructFields(this.fields, (Map<String, Object>) m, typeParameters);
        } else {
            return _ValidateUtil.getTypeUnexpectedValidationFailure(List.of(), value, this.getName(generics));
        }
    }

    public static List<_ValidationFailure> validateStructFields(
            Map<String, _UFieldDeclaration> fields,
            Map<String, Object> actualStruct, List<_UTypeDeclaration> typeParameters) {
        final var validationFailures = new ArrayList<_ValidationFailure>();

        final var missingFields = new ArrayList<String>();
        for (final var entry : fields.entrySet()) {
            final var fieldName = entry.getKey();
            final var fieldDeclaration = entry.getValue();
            final boolean isOptional = fieldDeclaration.optional;
            if (!actualStruct.containsKey(fieldName) && !isOptional) {
                missingFields.add(fieldName);
            }
        }

        for (final var missingField : missingFields) {
            final var validationFailure = new _ValidationFailure(List.of(missingField), "RequiredStructFieldMissing",
                    Map.of());

            validationFailures.add(validationFailure);
        }

        for (final var entry : actualStruct.entrySet()) {
            final var fieldName = entry.getKey();
            final var fieldValue = entry.getValue();

            final var referenceField = fields.get(fieldName);
            if (referenceField == null) {
                var validationFailure = new _ValidationFailure(List.of(fieldName), "StructFieldUnknown", Map.of());

                validationFailures.add(validationFailure);
                continue;
            }

            final _UTypeDeclaration refFieldTypeDeclaration = referenceField.typeDeclaration;

            final var nestedValidationFailures = refFieldTypeDeclaration.validate(fieldValue, typeParameters);

            final var nestedValidationFailuresWithPath = new ArrayList<_ValidationFailure>();
            for (final var f : nestedValidationFailures) {
                final List<Object> thisPath = _ValidateUtil.prepend(fieldName, f.path);

                nestedValidationFailuresWithPath.add(new _ValidationFailure(thisPath, f.reason, f.data));
            }

            validationFailures.addAll(nestedValidationFailuresWithPath);
        }

        return validationFailures;
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator random) {
        if (useStartingValue) {
            final var startingStructValue = (Map<String, Object>) startingValue;
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
            _RandomGenerator randomGenerator) {

        final var sortedReferenceStruct = new ArrayList<>(referenceStruct.entrySet());
        Collections.sort(sortedReferenceStruct, (e1, e2) -> e1.getKey().compareTo(e2.getKey()));

        final var obj = new TreeMap<String, Object>();
        for (final var field : sortedReferenceStruct) {
            final var fieldName = field.getKey();
            final var fieldDeclaration = field.getValue();
            final var startingValue = startingStruct.get(fieldName);
            final var useStartingValue = startingStruct.containsKey(fieldName);

            final Object value;
            if (useStartingValue) {
                value = fieldDeclaration.typeDeclaration.generateRandomValue(startingValue, useStartingValue,
                        includeRandomOptionalFields, typeParameters, randomGenerator);
            } else {
                if (!fieldDeclaration.optional) {
                    value = fieldDeclaration.typeDeclaration.generateRandomValue(null, false,
                            includeRandomOptionalFields, typeParameters, randomGenerator);
                } else {
                    if (!includeRandomOptionalFields) {
                        continue;
                    }
                    if (randomGenerator.nextBoolean()) {
                        continue;
                    }
                    value = fieldDeclaration.typeDeclaration.generateRandomValue(null, false,
                            includeRandomOptionalFields, typeParameters, randomGenerator);
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
