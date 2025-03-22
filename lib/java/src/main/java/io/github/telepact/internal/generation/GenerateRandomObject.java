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

import java.util.List;
import java.util.Map;
import java.util.TreeMap;

import io.github.telepact.internal.types.TTypeDeclaration;

public class GenerateRandomObject {
    public static Object generateRandomObject(Object blueprintValue, boolean useBlueprintValue,
            List<TTypeDeclaration> typeParameters, GenerateContext ctx) {
        final var nestedTypeDeclaration = typeParameters.get(0);

        if (useBlueprintValue) {
            final var startingObj = (Map<String, Object>) blueprintValue;

            final var obj = new TreeMap<String, Object>();
            for (final var startingObjEntry : startingObj.entrySet()) {
                final var key = startingObjEntry.getKey();
                final var startingObjValue = startingObjEntry.getValue();
                final var value = nestedTypeDeclaration
                        .generateRandomValue(startingObjValue, useBlueprintValue, ctx);
                obj.put(key, value);
            }

            return obj;
        } else {
            final var length = ctx.randomGenerator.nextCollectionLength();

            final var obj = new TreeMap<String, Object>();
            for (int i = 0; i < length; i += 1) {
                final var key = ctx.randomGenerator.nextString();
                final var value = nestedTypeDeclaration.generateRandomValue(null, false, ctx);
                obj.put(key, value);
            }

            return obj;
        }
    }
}
