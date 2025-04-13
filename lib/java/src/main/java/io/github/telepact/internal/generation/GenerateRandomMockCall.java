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
import java.util.stream.Collectors;

import io.github.telepact.internal.types.TType;
import io.github.telepact.internal.types.TUnion;

public class GenerateRandomMockCall {

    public static Object generateRandomMockCall(Map<String, TType> types, GenerateContext ctx) {
        List<String> functionNames = types.keySet().stream()
                .filter(key -> key.startsWith("fn.") && !key.endsWith(".->"))
                .filter(key -> !key.endsWith("_"))
                .sorted((fn1, fn2) -> fn1.compareTo(fn2))
                .collect(Collectors.toList());

        String selectedFnName = functionNames.get(ctx.randomGenerator.nextIntWithCeiling(functionNames.size()));
        TUnion selectedFn = (TUnion) types.get(selectedFnName);

        return GenerateRandomUnion.generateRandomUnion(null, false, selectedFn.tags,
                ctx.copyWithNewAlwaysIncludeRequiredFields(false));
    }
}
