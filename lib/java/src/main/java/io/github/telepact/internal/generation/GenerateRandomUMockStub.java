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

import static io.github.telepact.internal.generation.GenerateRandomStruct.generateRandomStruct;

import java.util.*;
import java.util.stream.Collectors;

import io.github.telepact.internal.types.VFn;
import io.github.telepact.internal.types.VType;

public class GenerateRandomUMockStub {

        public static Map<String, Object> generateRandomUMockStub(Map<String, VType> types, GenerateContext ctx) {
                List<VFn> functions = types.entrySet().stream()
                                .filter(entry -> entry.getValue() instanceof VFn)
                                .filter(entry -> !entry.getKey().endsWith("_"))
                                .map(entry -> (VFn) entry.getValue())
                                .sorted(Comparator.comparing(VFn::getName))
                                .collect(Collectors.toList());

                int index = ctx.randomGenerator.nextIntWithCeiling(functions.size());

                System.out.println("index: " + index);

                VFn selectedFn = functions.get(index);

                System.out.println("selectedFn: " + selectedFn.name);

                var argFields = selectedFn.call.tags.get(selectedFn.name).fields;
                var okFields = selectedFn.result.tags.get("Ok_").fields;

                var arg = generateRandomStruct(null, false, argFields,
                                ctx.copyWithNewAlwaysIncludeRequiredFields(false));
                var okResult = generateRandomStruct(null, false, okFields,
                                ctx.copyWithNewAlwaysIncludeRequiredFields(false));

                return Map.ofEntries(
                                Map.entry(selectedFn.name, arg),
                                Map.entry("->", Map.of("Ok_", okResult)));
        }
}
