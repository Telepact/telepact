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

package io.github.telepact.internal.mock;

import static io.github.telepact.internal.mock.IsSubMap.isSubMap;
import static io.github.telepact.internal.mock.Verify.verify;
import static io.github.telepact.internal.mock.VerifyNoMoreInteractions.verifyNoMoreInteractions;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.TreeMap;

import io.github.telepact.Message;
import io.github.telepact.TelepactError;
import io.github.telepact.TelepactSchema;
import io.github.telepact.RandomGenerator;
import io.github.telepact.internal.generation.GenerateContext;
import io.github.telepact.internal.types.TUnion;

public class MockHandle {
    public static Message handleCreateStub(Message requestMessage, List<MockStub> stubs) {
        final Map<String, Object> argument = requestMessage.getBodyPayload();
        final var givenStub = (Map<String, Object>) argument.get("stub");

        final var stubCall = givenStub.entrySet().stream().filter(e -> e.getKey().startsWith("fn."))
                .findAny().get();
        final var stubFunctionName = stubCall.getKey();
        final var stubArg = (Map<String, Object>) stubCall.getValue();
        final var stubResult = (Map<String, Object>) givenStub.get("->");
        final var allowArgumentPartialMatch = !((Boolean) argument.getOrDefault("strictMatch!", false));
        final var stubCount = (Integer) argument.getOrDefault("count!", -1);

        final var stub = new MockStub(stubFunctionName, new TreeMap<>(stubArg), stubResult,
                allowArgumentPartialMatch, stubCount);

        stubs.add(0, stub);
        return new Message(Map.of(), Map.of("Ok_", Map.of()));
    }

    public static Message handleVerify(Message requestMessage, List<MockInvocation> invocations) {
        final Map<String, Object> argument = requestMessage.getBodyPayload();
        final var givenCall = (Map<String, Object>) argument.get("call");

        final var call = givenCall.entrySet().stream().filter(e -> e.getKey().startsWith("fn."))
                .findAny().get();
        final var callFunctionName = call.getKey();
        final var callArg = (Map<String, Object>) call.getValue();
        final var verifyTimes = (Map<String, Object>) argument.getOrDefault("count!",
                Map.of("AtLeast", Map.of("times", 1)));
        final var strictMatch = (Boolean) argument.getOrDefault("strictMatch!", false);

        final var verificationResult = verify(callFunctionName, callArg, strictMatch,
                verifyTimes,
                invocations);
        return new Message(Map.of(), verificationResult);
    }

    public static Message handleVerifyNoMoreInteractions(List<MockInvocation> invocations) {
        final var verificationResult = verifyNoMoreInteractions(invocations);
        return new Message(Map.of(), verificationResult);
    }

    public static Message handleClearCalls(List<MockInvocation> invocations) {
        invocations.clear();
        return new Message(Map.of(), Map.of("Ok_", Map.of()));
    }

    public static Message handleClearStubs(List<MockStub> stubs) {
        stubs.clear();
        return new Message(Map.of(), Map.of("Ok_", Map.of()));
    }

    public static Message handleSetRandomSeed(Message requestMessage, RandomGenerator random) {
        final Map<String, Object> argument = requestMessage.getBodyPayload();
        final var givenSeed = (Integer) argument.get("seed");

        random.setSeed(givenSeed);
        return new Message(Map.of(), Map.of("Ok_", Map.of()));
    }

    public static Message handleAutoMockFunction(Message requestMessage, List<MockStub> stubs, List<MockInvocation> invocations,
            RandomGenerator random, TelepactSchema telepactSchema, boolean enableGeneratedDefaultStub,
            boolean enableOptionalFieldGeneration, boolean randomizeOptionalFieldGeneration) {
        final Map<String, Object> header = requestMessage.headers;

        final var enableGenerationStub = (Boolean) header.getOrDefault(".gen_", false);
        final String functionName = requestMessage.getBodyTarget();
        final Map<String, Object> argument = requestMessage.getBodyPayload();

        invocations.add(new MockInvocation(functionName, new TreeMap<>(argument)));

        final var definition = (TUnion) telepactSchema.parsed.get(functionName + ".->");

        for (final var stub : stubs) {
            if (stub.count == 0) {
                continue;
            }
            if (Objects.equals(stub.whenFunction, functionName)) {
                if (stub.allowArgumentPartialMatch) {
                    if (isSubMap(stub.whenArgument, argument)) {
                        final var useBlueprintValue = true;
                        final var includeOptionalFields = false;
                        final var alwaysIncludeRequiredFields = true;
                        final var result = (Map<String, Object>) definition.generateRandomValue(
                                stub.thenResult, useBlueprintValue, List.of(),
                                new GenerateContext(
                                        includeOptionalFields, randomizeOptionalFieldGeneration,
                                        alwaysIncludeRequiredFields, functionName,
                                        random));
                        if (stub.count > 0) {
                            stub.count -= 1;
                        }
                        return new Message(Map.of(), result);
                    }
                } else {
                    if (Objects.equals(stub.whenArgument, argument)) {
                        final var useBlueprintValue = true;
                        final var includeOptionalFields = false;
                        final var alwaysIncludeRequiredFields = true;
                        final var result = (Map<String, Object>) definition.generateRandomValue(
                                stub.thenResult, useBlueprintValue, List.of(),
                                new GenerateContext(
                                        includeOptionalFields, randomizeOptionalFieldGeneration,
                                        alwaysIncludeRequiredFields, functionName,
                                        random));
                        if (stub.count > 0) {
                            stub.count -= 1;
                        }
                        return new Message(Map.of(), result);
                    }
                }
            }
        }

        if (!enableGeneratedDefaultStub && !enableGenerationStub) {
            return new Message(Map.of(), Map.of("ErrorNoMatchingStub_", Map.of()));
        }

        if (definition != null) {
            final var resultUnion = (TUnion) definition;
            final var okStructRef = resultUnion.tags.get("Ok_");
            final var useBlueprintValue = true;
            final var includeOptionalFields = enableOptionalFieldGeneration;
            final var alwaysIncludeRequiredFields = true;
            final var randomOkStruct = okStructRef
                    .generateRandomValue(new HashMap<>(), useBlueprintValue, List.of(),
                            new GenerateContext(
                                    includeOptionalFields, randomizeOptionalFieldGeneration,
                                    alwaysIncludeRequiredFields, functionName, random));
            return new Message(Map.of(), Map.of("Ok_", randomOkStruct));
        } else {
            throw new TelepactError("Unexpected unknown function: %s".formatted(functionName));
        }
    }
}
