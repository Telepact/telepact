//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.generation;

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

            return selectedFieldNames.stream().sorted().toList();
        } else if (possibleSelectSection instanceof Map) {
            final var m = (Map<String, Object>) possibleSelectSection;
            Map<String, Object> selectedSection = new HashMap<>();

            List<String> keys = m.keySet().stream().sorted().toList();

            for (String key : keys) {
                final var value = m.get(key);
                if (ctx.randomGenerator.nextBoolean()) {
                    Object result = subSelect(value, ctx);
                    if (result instanceof Map && ((Map<?, ?>) result).isEmpty()) {
                        continue;
                    }
                    selectedSection.put(key, result);
                }
            }

            return selectedSection;
        } else {
            throw new IllegalArgumentException("Invalid possibleSelectSection");
        }
    }
}
