package io.github.brenbar.uapi;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.TreeMap;

class _MockServerUtil {

    static Message handle(Message requestMessage, List<_MockStub> stubs,
            List<Invocation> invocations, RandomGenerator random, UApiSchema jApiSchema,
            boolean enableGeneratedDefaultStub) {

        var enableGenerationStub = (Boolean) requestMessage.header.getOrDefault("_mockEnableGeneratedStub", false);
        var functionName = requestMessage.getBodyTarget();
        var argument = requestMessage.getBodyPayload();

        switch (functionName) {
            case "fn._createStub" -> {
                var givenStub = (Map<String, Object>) argument.get("stub");

                var stubCall = givenStub.entrySet().stream().filter(e -> e.getKey().startsWith("fn."))
                        .findAny().get();
                var stubFunctionName = stubCall.getKey();
                var stubArg = (Map<String, Object>) stubCall.getValue();
                var stubResult = (Map<String, Object>) givenStub.get("->");
                var allowArgumentPartialMatch = !((Boolean) argument.getOrDefault("strictMatch!", false));

                var stub = new _MockStub(stubFunctionName, new TreeMap<>(stubArg), stubResult,
                        allowArgumentPartialMatch);

                stubs.add(0, stub);
                return new Message(Map.of("Ok", Map.of()));
            }
            case "fn._verify" -> {
                var givenCall = (Map<String, Object>) argument.get("call");

                var call = givenCall.entrySet().stream().filter(e -> e.getKey().startsWith("fn."))
                        .findAny().get();
                var callFunctionName = call.getKey();
                var callArg = (Map<String, Object>) call.getValue();
                var verifyTimes = (Map<String, Object>) argument.getOrDefault("count!",
                        Map.of("AtLeast", Map.of("times", 1)));
                var strictMatch = (Boolean) argument.getOrDefault("strictMatch!", false);

                var verificationResult = _MockVerifyUtil.verify(callFunctionName, callArg, strictMatch,
                        verifyTimes,
                        invocations);
                return new Message(verificationResult);
            }
            case "fn._verifyNoMoreInteractions" -> {
                var verificationResult = _MockVerifyUtil.verifyNoMoreInteractions(invocations);
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
                var givenSeed = (Integer) argument.get("seed");

                random.setSeed(givenSeed);
                return new Message(Map.of("Ok", Map.of()));
            }
            default -> {
                invocations.add(new Invocation(functionName, new TreeMap<>(argument)));

                var definition = (_UFn) jApiSchema.parsed.get(functionName);

                for (var stub : stubs) {
                    if (Objects.equals(stub.whenFunction, functionName)) {
                        if (stub.allowArgumentPartialMatch) {
                            if (isSubMap(stub.whenArgument, argument)) {
                                var useStartingValue = true;
                                var includeRandomOptionalFields = false;
                                var result = (Map<String, Object>) definition.result.generateRandomValue(
                                        stub.thenResult, useStartingValue,
                                        includeRandomOptionalFields, List.of(), List.of(), random);
                                return new Message(result);
                            }
                        } else {
                            if (Objects.equals(stub.whenArgument, argument)) {
                                var useStartingValue = true;
                                var includeRandomOptionalFields = false;
                                var result = (Map<String, Object>) definition.result.generateRandomValue(
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
                    var resultUnion = (_UUnion) definition.result;
                    var OkStructRef = resultUnion.cases.get("Ok");
                    var useStartingValue = true;
                    var includeRandomOptionalFields = true;
                    var randomOkStruct = OkStructRef.generateRandomValue(new HashMap<>(), useStartingValue,
                            includeRandomOptionalFields, List.of(), List.of(), random);
                    return new Message(Map.of("Ok", randomOkStruct));
                } else {
                    throw new UApiProcessError("Unexpected unknown function: %s".formatted(functionName));
                }
            }
        }
    }

    static boolean isSubMap(Map<String, Object> part, Map<String, Object> whole) {
        for (var partKey : part.keySet()) {
            var wholeValue = whole.get(partKey);
            var partValue = part.get(partKey);
            var entryIsEqual = isSubMapEntryEqual(partValue, wholeValue);
            if (!entryIsEqual) {
                return false;
            }
        }
        return true;
    }

    private static boolean isSubMapEntryEqual(Object partValue, Object wholeValue) {
        if (partValue instanceof Map m1 && wholeValue instanceof Map m2) {
            return isSubMap(m1, m2);
        } else if (partValue instanceof List partList && wholeValue instanceof List wholeList) {
            for (int i = 0; i < partList.size(); i += 1) {
                var partElement = partList.get(i);
                var partMatches = false;
                for (var wholeElement : wholeList) {
                    if (isSubMapEntryEqual(partElement, wholeElement)) {
                        partMatches = true;
                        break;
                    }
                }
                if (!partMatches) {
                    return false;
                }
            }
            return true;
        } else {
            return Objects.equals(partValue, wholeValue);
        }
    }

}
