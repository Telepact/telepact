package io.github.msgpact.internal.generation;

import java.util.*;

public class GenerateRandomSelect {

    public static Object generateRandomSelect(Map<String, Object> possibleSelects, GenerateContext ctx) {
        var possibleSelect = possibleSelects.get(ctx.fnScope);
        return subSelect(possibleSelect, ctx);
    }

    private static Object subSelect(Object possibleSelectSection, GenerateContext ctx) {
        if (possibleSelectSection instanceof List) {
            List<String> selectedFieldNames = new ArrayList<>();

            for (Object fieldName : (List<?>) possibleSelectSection) {
                if (ctx.randomGenerator.nextBoolean()) {
                    selectedFieldNames.add((String) fieldName);
                }
            }

            return selectedFieldNames;
        } else if (possibleSelectSection instanceof Map) {
            Map<String, Object> selectedSection = new HashMap<>();

            for (Map.Entry<String, Object> entry : ((Map<String, Object>) possibleSelectSection).entrySet()) {
                if (ctx.randomGenerator.nextBoolean()) {
                    Object result = subSelect(entry.getValue(), ctx);
                    if (result instanceof Map && ((Map<?, ?>) result).isEmpty()) {
                        continue;
                    }
                    selectedSection.put(entry.getKey(), result);
                }
            }

            return selectedSection;
        } else {
            throw new IllegalArgumentException("Invalid possibleSelectSection");
        }
    }
}
