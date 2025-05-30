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

import io.github.telepact.internal.types.TType;
import io.github.telepact.internal.types.TTypeDeclaration;

public class GenerateRandomValueOfType {
    public static Object generateRandomValueOfType(Object blueprintValue, boolean useBlueprintValue, TType thisType,
            boolean nullable,
            List<TTypeDeclaration> typeParameters, GenerateContext ctx) {
        if (nullable && !useBlueprintValue && ctx.randomGenerator.nextBoolean()) {
            return null;
        } else {
            return thisType.generateRandomValue(blueprintValue, useBlueprintValue, typeParameters, ctx);
        }
    }
}
