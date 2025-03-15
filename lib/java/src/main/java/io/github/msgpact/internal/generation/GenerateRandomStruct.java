package io.github.msgpact.internal.generation;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.TreeMap;

import io.github.msgpact.internal.types.VFieldDeclaration;
import io.github.msgpact.internal.types.VTypeDeclaration;

public class GenerateRandomStruct {
    public static Object generateRandomStruct(
            Object blueprintValue, boolean useBlueprintValue,
            Map<String, VFieldDeclaration> referenceStruct,
            GenerateContext ctx) {
        final var startingStruct = useBlueprintValue ? (Map<String, Object>) blueprintValue : new HashMap<>();

        final var sortedReferenceStruct = new ArrayList<>(referenceStruct.entrySet());
        Collections.sort(sortedReferenceStruct, (e1, e2) -> e1.getKey().compareTo(e2.getKey()));

        final var obj = new TreeMap<String, Object>();
        for (final var field : sortedReferenceStruct) {
            final var fieldName = field.getKey();
            final var fieldDeclaration = field.getValue();
            final var thisBlueprintValue = startingStruct.get(fieldName);
            final var thisUseBlueprintValue = startingStruct.containsKey(fieldName);
            final VTypeDeclaration typeDeclaration = fieldDeclaration.typeDeclaration;

            final Object value;
            if (thisUseBlueprintValue) {
                value = typeDeclaration.generateRandomValue(
                        thisBlueprintValue, thisUseBlueprintValue, ctx);
            } else {
                if (!fieldDeclaration.optional) {
                    if (!ctx.alwaysIncludeRequiredFields && ctx.randomGenerator.nextBoolean()) {
                        continue;
                    }
                    value = typeDeclaration
                            .generateRandomValue(null, false, ctx);
                } else {
                    if (!ctx.includeOptionalFields
                            || (ctx.randomizeOptionalFields && ctx.randomGenerator.nextBoolean())) {
                        continue;
                    }
                    value = typeDeclaration
                            .generateRandomValue(null, false, ctx);
                }
            }

            obj.put(fieldName, value);
        }
        return obj;
    }
}
