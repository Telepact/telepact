package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.TreeMap;

import io.github.brenbar.japi.MockVerification.AtLeastNumberOfTimes;
import io.github.brenbar.japi.MockVerification.AtMostNumberOfTimes;
import io.github.brenbar.japi.MockVerification.ExactNumberOfTimes;
import io.github.brenbar.japi.MockVerification.VerificationTimes;

class _MockServerUtil {

    static Message handle(Message requestMessage, List<MockStub> stubs,
            List<Invocation> invocations, RandomGenerator random, JApiSchema jApiSchema,
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
                var allowArgumentPartialMatch = !((Boolean) argument.getOrDefault("strictMatch", false));

                var stub = new MockStub(stubFunctionName, new TreeMap<>(stubArg), stubResult);
                if (allowArgumentPartialMatch) {
                    stub.setAllowArgumentPartialMatch(allowArgumentPartialMatch);
                }

                stubs.add(0, stub);
                return new Message(Map.of("Ok", Map.of()));
            }
            case "fn._verify" -> {
                var givenCall = (Map<String, Object>) argument.get("call");

                var call = givenCall.entrySet().stream().filter(e -> e.getKey().startsWith("fn."))
                        .findAny().get();
                var callFunctionName = call.getKey();
                var callArg = (Map<String, Object>) call.getValue();
                var verifyTimes = (Map<String, Object>) argument.getOrDefault("count",
                        Map.of("AtLeast", Map.of("times", 1)));
                var strictMatch = (Boolean) argument.getOrDefault("strictMatch", false);

                var verificationTimes = parseFromPseudoJson(verifyTimes);

                var verificationResult = verify(callFunctionName, callArg, strictMatch,
                        verificationTimes,
                        invocations);
                return new Message(verificationResult);
            }
            case "fn._verifyNoMoreInteractions" -> {
                var verificationResult = verifyNoMoreInteractions(invocations);
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
            default -> {
                invocations.add(new Invocation(functionName, new TreeMap<>(argument)));

                var definition = (UFn) jApiSchema.parsed.get(functionName);

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
                    var resultEnum = (UEnum) definition.result;
                    var OkStructRef = resultEnum.values.get("Ok");
                    var useStartingValue = true;
                    var includeRandomOptionalFields = true;
                    var randomOkStruct = OkStructRef.generateRandomValue(new HashMap<>(), useStartingValue,
                            includeRandomOptionalFields, List.of(), List.of(), random);
                    return new Message(Map.of("Ok", randomOkStruct));
                } else {
                    throw new JApiProcessError("Unexpected unknown function: %s".formatted(functionName));
                }
            }
        }
    }

    static VerificationTimes parseFromPseudoJson(Map<String, Object> verifyTimes) {
        var verifyTimesEntry = verifyTimes.entrySet().stream().findAny().get();
        var verifyTimesStruct = (Map<String, Object>) verifyTimesEntry.getValue();
        return switch (verifyTimesEntry.getKey()) {
            case "unlimited" -> new MockVerification.UnlimitedNumberOfTimes();
            case "Exact" -> {
                var times = (Integer) verifyTimesStruct.get("times");
                yield new MockVerification.ExactNumberOfTimes(times);
            }
            case "AtMost" -> {
                var times = (Integer) verifyTimesStruct.get("times");
                yield new MockVerification.AtMostNumberOfTimes(times);
            }
            case "AtLeast" -> {
                var times = (Integer) verifyTimesStruct.get("times");
                yield new MockVerification.AtLeastNumberOfTimes(times);
            }
            default -> throw new JApiProcessError("Unknown verification times");
        };
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

    static Map<String, Object> verify(String functionName, Map<String, Object> argument,
            boolean exactMatch,
            VerificationTimes verificationTimes, List<Invocation> invocations) {
        var matchesFound = 0;
        for (var invocation : invocations) {
            if (Objects.equals(invocation.functionName, functionName)) {
                if (exactMatch) {
                    if (Objects.equals(invocation.functionArgument, argument)) {
                        invocation.verified = true;
                        matchesFound += 1;
                    }
                } else {
                    if (_MockServerUtil.isSubMap(argument, invocation.functionArgument)) {
                        invocation.verified = true;
                        matchesFound += 1;
                    }
                }
            }
        }

        var allCallsPseudoJson = new ArrayList<Map<String, Object>>();
        for (var invocation : invocations) {
            allCallsPseudoJson.add(Map.of(invocation.functionName, invocation.functionArgument));
        }
        Map<String, Object> verificationFailurePseudoJson = null;
        if (verificationTimes instanceof ExactNumberOfTimes e) {
            if (matchesFound > e.times) {
                verificationFailurePseudoJson = Map.of("TooManyMatchingCalls",
                        new TreeMap<>(Map.ofEntries(
                                Map.entry("wanted", Map.of("Exact", Map.of("times", e.times))),
                                Map.entry("found", matchesFound),
                                Map.entry("allCalls", allCallsPseudoJson))));
            } else if (matchesFound < e.times) {
                verificationFailurePseudoJson = Map.of("TooFewMatchingCalls",
                        new TreeMap<>(Map.ofEntries(
                                Map.entry("wanted", Map.of("Exact", Map.of("times", e.times))),
                                Map.entry("found", matchesFound),
                                Map.entry("allCalls", allCallsPseudoJson))));
            }
        } else if (verificationTimes instanceof AtMostNumberOfTimes a) {
            if (matchesFound > a.times) {
                verificationFailurePseudoJson = Map.of("TooManyMatchingCalls",
                        new TreeMap<>(Map.ofEntries(
                                Map.entry("wanted", Map.of("AtMost", Map.of("times", a.times))),
                                Map.entry("found", matchesFound),
                                Map.entry("allCalls", allCallsPseudoJson))));
            }
        } else if (verificationTimes instanceof AtLeastNumberOfTimes a) {
            if (matchesFound < a.times) {
                verificationFailurePseudoJson = Map.of("TooFewMatchingCalls",
                        new TreeMap<>(Map.ofEntries(
                                Map.entry("wanted", Map.of("AtLeast", Map.of("times", a.times))),
                                Map.entry("found", matchesFound),
                                Map.entry("allCalls", allCallsPseudoJson))));

            }
        } else {
            throw new JApiProcessError("Unexpected verification times");
        }

        if (verificationFailurePseudoJson == null) {
            return Map.of("Ok", Map.of());
        }

        return Map.of("ErrorVerificationFailure", Map.of("reason", verificationFailurePseudoJson));
    }

    static Map<String, Object> verifyNoMoreInteractions(List<Invocation> invocations) {
        var invocationsNotVerified = invocations.stream().filter(i -> !i.verified).toList();

        if (invocationsNotVerified.size() > 0) {
            var unverifiedCallsPseudoJson = new ArrayList<Map<String, Object>>();
            for (var invocation : invocationsNotVerified) {
                unverifiedCallsPseudoJson.add(Map.of(invocation.functionName, invocation.functionArgument));
            }
            return Map.of("ErrorVerificationFailure",
                    Map.of("additionalUnverifiedCalls", unverifiedCallsPseudoJson));
        }

        return Map.of("Ok", Map.of());
    }
}
