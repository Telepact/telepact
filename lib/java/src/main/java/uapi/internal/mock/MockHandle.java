package uapi.internal.mock;

import static uapi.internal.mock.IsSubMap.isSubMap;
import static uapi.internal.mock.Verify.verify;
import static uapi.internal.mock.VerifyNoMoreInteractions.verifyNoMoreInteractions;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.TreeMap;

import uapi.Message;
import uapi.RandomGenerator;
import uapi.UApiError;
import uapi.UApiSchema;
import uapi.internal.generation.GenerateContext;
import uapi.internal.types.UFn;
import uapi.internal.types.UUnion;

public class MockHandle {
    public static Message mockHandle(Message requestMessage, List<MockStub> stubs, List<MockInvocation> invocations,
            RandomGenerator random, UApiSchema uApiSchema, boolean enableGeneratedDefaultStub,
            boolean enableOptionalFieldGeneration, boolean randomizeOptionalFieldGeneration) {
        final Map<String, Object> header = requestMessage.header;

        final var enableGenerationStub = (Boolean) header.getOrDefault("_gen", false);
        final String functionName = requestMessage.getBodyTarget();
        final Map<String, Object> argument = requestMessage.getBodyPayload();

        switch (functionName) {
            case "fn.createStub_" -> {
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
            case "fn.verify_" -> {
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
            case "fn.verifyNoMoreInteractions_" -> {
                final var verificationResult = verifyNoMoreInteractions(invocations);
                return new Message(Map.of(), verificationResult);
            }
            case "fn.clearCalls_" -> {
                invocations.clear();
                return new Message(Map.of(), Map.of("Ok_", Map.of()));
            }
            case "fn.clearStubs_" -> {
                stubs.clear();
                return new Message(Map.of(), Map.of("Ok_", Map.of()));
            }
            case "fn.setRandomSeed_" -> {
                final var givenSeed = (Integer) argument.get("seed");

                random.setSeed(givenSeed);
                return new Message(Map.of(), Map.of("Ok_", Map.of()));
            }
            default -> {
                invocations.add(new MockInvocation(functionName, new TreeMap<>(argument)));

                final var definition = (UFn) uApiSchema.parsed.get(functionName);

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
                                final var result = (Map<String, Object>) definition.result.generateRandomValue(
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
                                final var result = (Map<String, Object>) definition.result.generateRandomValue(
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
                    final var resultUnion = (UUnion) definition.result;
                    final var okStructRef = resultUnion.tags.get("Ok_");
                    final var useBlueprintValue = true;
                    final var includeOptionalFields = true;
                    final var alwaysIncludeRequiredFields = true;
                    final var randomOkStruct = okStructRef
                            .generateRandomValue(new HashMap<>(), useBlueprintValue, List.of(),
                                    new GenerateContext(
                                            includeOptionalFields, randomizeOptionalFieldGeneration,
                                            alwaysIncludeRequiredFields, functionName, random));
                    return new Message(Map.of(), Map.of("Ok_", randomOkStruct));
                } else {
                    throw new UApiError("Unexpected unknown function: %s".formatted(functionName));
                }
            }
        }
    }
}
