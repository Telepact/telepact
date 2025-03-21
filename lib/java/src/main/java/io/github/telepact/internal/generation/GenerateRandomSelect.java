//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
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
