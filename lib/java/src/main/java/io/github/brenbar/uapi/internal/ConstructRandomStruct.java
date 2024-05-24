package io.github.brenbar.uapi.internal;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

import io.github.brenbar.uapi.RandomGenerator;

public class ConstructRandomStruct {
    static Map<String, Object> constructRandomStruct(
            Map<String, UFieldDeclaration> referenceStruct, Map<String, Object> startingStruct,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<UTypeDeclaration> typeParameters,
            RandomGenerator randomGenerator) {

        final var sortedReferenceStruct = new ArrayList<>(referenceStruct.entrySet());
        Collections.sort(sortedReferenceStruct, (e1, e2) -> e1.getKey().compareTo(e2.getKey()));

        final var obj = new TreeMap<String, Object>();
        for (final var field : sortedReferenceStruct) {
            final var fieldName = field.getKey();
            final var fieldDeclaration = field.getValue();
            final var blueprintValue = startingStruct.get(fieldName);
            final var useBlueprintValue = startingStruct.containsKey(fieldName);
            final UTypeDeclaration typeDeclaration = fieldDeclaration.typeDeclaration;

            final Object value;
            if (useBlueprintValue) {
                value = typeDeclaration.generateRandomValue(blueprintValue, useBlueprintValue,
                        includeOptionalFields, randomizeOptionalFields, typeParameters, randomGenerator);
            } else {
                if (!fieldDeclaration.optional) {
                    value = typeDeclaration.generateRandomValue(null, false,
                            includeOptionalFields, randomizeOptionalFields, typeParameters, randomGenerator);
                } else {
                    if (!includeOptionalFields || (randomizeOptionalFields && randomGenerator.nextBoolean())) {
                        continue;
                    }
                    value = typeDeclaration.generateRandomValue(null, false,
                            includeOptionalFields, randomizeOptionalFields, typeParameters, randomGenerator);
                }
            }

            obj.put(fieldName, value);
        }
        return obj;
    }
}
