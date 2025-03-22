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

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.TreeMap;

import io.github.telepact.internal.types.TFieldDeclaration;
import io.github.telepact.internal.types.TTypeDeclaration;

public class GenerateRandomStruct {
    public static Object generateRandomStruct(
            Object blueprintValue, boolean useBlueprintValue,
            Map<String, TFieldDeclaration> referenceStruct,
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
            final TTypeDeclaration typeDeclaration = fieldDeclaration.typeDeclaration;

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
