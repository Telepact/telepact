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

import io.github.telepact.internal.types.TFn;
import io.github.telepact.internal.types.TType;

public class GenerateRandomMockCall {

    public static Object generateRandomMockCall(Map<String, TType> types, GenerateContext ctx) {
        List<TFn> functions = types.entrySet().stream()
                .filter(entry -> entry.getValue() instanceof TFn)
                .filter(entry -> !entry.getKey().endsWith("_"))
                .map(entry -> (TFn) entry.getValue())
                .sorted((fn1, fn2) -> fn1.name.compareTo(fn2.name))
                .collect(Collectors.toList());

        TFn selectedFn = functions.get(ctx.randomGenerator.nextIntWithCeiling(functions.size()));

        return GenerateRandomUnion.generateRandomUnion(null, false, selectedFn.call.tags,
                ctx.copyWithNewAlwaysIncludeRequiredFields(false));
    }
}
