package uapi.internal.generation;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.TreeMap;

import uapi.internal.types.UFieldDeclaration;
import uapi.internal.types.UTypeDeclaration;

public class GenerateRandomStruct {
    public static Object generateRandomStruct(
            Map<String, UFieldDeclaration> referenceStruct, GenerateContext ctx) {
        final var startingStruct = ctx.useBlueprintValue ? (Map<String, Object>) ctx.blueprintValue : new HashMap<>();

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
                value = typeDeclaration.generateRandomValue(
                        ctx.copyWithNewBlueprintValueAndUseBlueprintValue(blueprintValue, useBlueprintValue));
            } else {
                if (!fieldDeclaration.optional) {
                    value = typeDeclaration
                            .generateRandomValue(ctx.copyWithNewBlueprintValueAndUseBlueprintValue(null, false));
                } else {
                    if (!ctx.includeOptionalFields
                            || (ctx.randomizeOptionalFields && ctx.randomGenerator.nextBoolean())) {
                        continue;
                    }
                    value = typeDeclaration
                            .generateRandomValue(ctx.copyWithNewBlueprintValueAndUseBlueprintValue(null, false));
                }
            }

            obj.put(fieldName, value);
        }
        return obj;
    }
}
