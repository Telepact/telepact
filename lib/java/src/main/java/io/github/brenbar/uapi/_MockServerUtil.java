package io.github.brenbar.uapi;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.TreeMap;

class _MockServerUtil {

    static Message handle(Message requestMessage, List<_MockStub> stubs, List<_MockInvocation> invocations,
            _RandomGenerator random, UApiSchema uApiSchema, boolean enableGeneratedDefaultStub) {
        final Map<String, Object> header = requestMessage.header;

        final var enableGenerationStub = (Boolean) header.getOrDefault("_mockEnableGeneratedStub", false);
        final String functionName = requestMessage.getBodyTarget();
        final Map<String, Object> argument = requestMessage.getBodyPayload();

        switch (functionName) {
            case "fn._createStub" -> {
                final var givenStub = (Map<String, Object>) argument.get("stub");

                final var stubCall = givenStub.entrySet().stream().filter(e -> e.getKey().startsWith("fn."))
                        .findAny().get();
                final var stubFunctionName = stubCall.getKey();
                final var stubArg = (Map<String, Object>) stubCall.getValue();
                final var stubResult = (Map<String, Object>) givenStub.get("->");
                final var allowArgumentPartialMatch = !((Boolean) argument.getOrDefault("strictMatch!", false));

                final var stub = new _MockStub(stubFunctionName, new TreeMap<>(stubArg), stubResult,
                        allowArgumentPartialMatch);

                stubs.add(0, stub);
                return new Message(Map.of("Ok", Map.of()));
            }
            case "fn._verify" -> {
                final var givenCall = (Map<String, Object>) argument.get("call");

                final var call = givenCall.entrySet().stream().filter(e -> e.getKey().startsWith("fn."))
                        .findAny().get();
                final var callFunctionName = call.getKey();
                final var callArg = (Map<String, Object>) call.getValue();
                final var verifyTimes = (Map<String, Object>) argument.getOrDefault("count!",
                        Map.of("AtLeast", Map.of("times", 1)));
                final var strictMatch = (Boolean) argument.getOrDefault("strictMatch!", false);

                final var verificationResult = _MockVerifyUtil.verify(callFunctionName, callArg, strictMatch,
                        verifyTimes,
                        invocations);
                return new Message(verificationResult);
            }
            case "fn._verifyNoMoreInteractions" -> {
                final var verificationResult = _MockVerifyUtil.verifyNoMoreInteractions(invocations);
                return new Message(verificationResult);
            }
            case "fn._clearCalls" -> {
                invocations.clear();
                return new Message(Map.of("Ok", Map.of()));
            }
            case "fn._clearStubs" -> {
                stubs.clear();
                return new Message(Map.of("Ok", Map.of()));
            }
            case "fn._setRandomSeed" -> {
                final var givenSeed = (Integer) argument.get("seed");

                random.setSeed(givenSeed);
                return new Message(Map.of("Ok", Map.of()));
            }
            default -> {
                invocations.add(new _MockInvocation(functionName, new TreeMap<>(argument)));

                final var definition = (_UFn) uApiSchema.parsed.get(functionName);

                for (final var stub : stubs) {
                    if (Objects.equals(stub.whenFunction, functionName)) {
                        if (stub.allowArgumentPartialMatch) {
                            if (isSubMap(stub.whenArgument, argument)) {
                                final var useStartingValue = true;
                                final var includeRandomOptionalFields = false;
                                final var result = (Map<String, Object>) definition.result.generateRandomValue(
                                        stub.thenResult, useStartingValue,
                                        includeRandomOptionalFields, List.of(), List.of(), random);
                                return new Message(result);
                            }
                        } else {
                            if (Objects.equals(stub.whenArgument, argument)) {
                                final var useStartingValue = true;
                                final var includeRandomOptionalFields = false;
                                final var result = (Map<String, Object>) definition.result.generateRandomValue(
                                        stub.thenResult, useStartingValue,
                                        includeRandomOptionalFields, List.of(), List.of(), random);
                                return new Message(result);
                            }
                        }
                    }
                }

                if (!enableGeneratedDefaultStub && !enableGenerationStub) {
                    return new Message(Map.of("_ErrorNoMatchingStub", Map.of()));
                }

                if (definition != null) {
                    final var resultUnion = (_UUnion) definition.result;
                    final var OkStructRef = resultUnion.cases.get("Ok");
                    final var useStartingValue = true;
                    final var includeRandomOptionalFields = true;
                    final var randomOkStruct = OkStructRef.generateRandomValue(new HashMap<>(), useStartingValue,
                            includeRandomOptionalFields, List.of(), List.of(), random);
                    return new Message(Map.of("Ok", randomOkStruct));
                } else {
                    throw new UApiProcessError("Unexpected unknown function: %s".formatted(functionName));
                }
            }
        }
    }

    static boolean isSubMap(Map<String, Object> part, Map<String, Object> whole) {
        for (final var partKey : part.keySet()) {
            final var wholeValue = whole.get(partKey);
            final var partValue = part.get(partKey);
            final var entryIsEqual = isSubMapEntryEqual(partValue, wholeValue);
            if (!entryIsEqual) {
                return false;
            }
        }
        return true;
    }

    private static boolean isSubMapEntryEqual(Object partValue, Object wholeValue) {
        if (partValue instanceof final Map m1 && wholeValue instanceof final Map m2) {
            return isSubMap(m1, m2);
        } else if (partValue instanceof final List partList && wholeValue instanceof final List wholeList) {
            for (int i = 0; i < partList.size(); i += 1) {
                final var partElement = partList.get(i);
                final var partMatches = partiallyMatches(wholeList, partElement);
                if (!partMatches) {
                    return false;
                }
            }

            return true;
        } else {
            return Objects.equals(partValue, wholeValue);
        }
    }

    private static boolean partiallyMatches(List<Object> wholeList, Object partElement) {
        for (final var wholeElement : wholeList) {
            if (isSubMapEntryEqual(partElement, wholeElement)) {
                return true;
            }
        }

        return false;
    }

}
