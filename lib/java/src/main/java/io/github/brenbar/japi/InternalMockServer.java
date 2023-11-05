package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.TreeMap;

import com.fasterxml.jackson.databind.ObjectMapper;

import io.github.brenbar.japi.MockVerification.AtLeastNumberOfTimes;
import io.github.brenbar.japi.MockVerification.AtMostNumberOfTimes;
import io.github.brenbar.japi.MockVerification.ExactNumberOfTimes;
import io.github.brenbar.japi.MockVerification.VerificationTimes;

class InternalMockServer {

    static Message handle(Message requestMessage, List<MockStub> stubs,
            List<Invocation> invocations, MockRandom random, JApiSchema jApiSchema,
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
                var allowArgumentPartialMatch = (Boolean) argument.getOrDefault("ignoreMissingArgFields", false);
                var randomFillMissingResultFields = (Boolean) argument.getOrDefault("generateMissingResultFields",
                        false);

                var stub = new MockStub(stubFunctionName, new TreeMap<>(stubArg), stubResult);
                if (allowArgumentPartialMatch) {
                    stub.setAllowArgumentPartialMatch(allowArgumentPartialMatch);
                }
                if (randomFillMissingResultFields) {
                    stub.setGenerateMissingResultFields(randomFillMissingResultFields);
                }

                stubs.add(0, stub);
                return new Message(Map.of("ok", Map.of()));
            }
            case "fn._verify" -> {
                var givenCall = (Map<String, Object>) argument.get("call");

                var call = givenCall.entrySet().stream().filter(e -> e.getKey().startsWith("fn."))
                        .findAny().get();
                var callFunctionName = call.getKey();
                var callArg = (Map<String, Object>) call.getValue();
                var verifyTimes = (Map<String, Object>) argument.getOrDefault("count",
                        Map.of("atLeast", Map.of("times", 1)));
                var allowArgumentPartialMatch = !((Boolean) argument.getOrDefault("strictMatch", true));

                var verificationTimes = parseFromPseudoJson(verifyTimes);

                var verificationResult = verify(callFunctionName, callArg, allowArgumentPartialMatch,
                        verificationTimes,
                        invocations);
                return new Message(verificationResult);
            }
            case "fn._verifyNoMoreInteractions" -> {
                var verificationResult = verifyNoMoreInteractions(invocations);
                return new Message(verificationResult);
            }
            case "fn._clearInvocations" -> {
                invocations.clear();
                return new Message(Map.of("ok", Map.of()));
            }
            case "fn._clearStubs" -> {
                stubs.clear();
                return new Message(Map.of("ok", Map.of()));
            }
            default -> {
                invocations.add(new Invocation(functionName, new TreeMap<>(argument)));

                for (var stub : stubs) {
                    if (Objects.equals(stub.whenFunction, functionName)) {
                        if (stub.allowArgumentPartialMatch) {
                            if (isSubMap(stub.whenArgument, argument)) {
                                return new Message(stub.thenResult);
                            }
                        } else {
                            if (Objects.equals(stub.whenArgument, argument)) {
                                return new Message(stub.thenResult);
                            }
                        }
                    }
                }

                if (!enableGeneratedDefaultStub && !enableGenerationStub) {
                    return new Message(Map.of("_errorNoMatchingStub", Map.of()));
                }

                var definition = (Fn) jApiSchema.parsed.get(functionName);

                if (definition != null) {
                    var resultEnum = (Enum) definition.result;
                    var okStructRef = resultEnum.values.get("ok");
                    var randomOkStruct = constructRandomStruct(okStructRef.fields, random);
                    return new Message(Map.of("ok", randomOkStruct));
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
            case "exact" -> {
                var times = (Integer) verifyTimesStruct.get("times");
                yield new MockVerification.ExactNumberOfTimes(times);
            }
            case "atMost" -> {
                var times = (Integer) verifyTimesStruct.get("times");
                yield new MockVerification.AtMostNumberOfTimes(times);
            }
            case "atLeast" -> {
                var times = (Integer) verifyTimesStruct.get("times");
                yield new MockVerification.AtLeastNumberOfTimes(times);
            }
            default -> throw new JApiProcessError("Unknown verification times");
        };
    }

    static boolean isSubMap(Map<String, Object> sub, Map<String, Object> reference) {
        for (var subKey : sub.keySet()) {
            var referenceValue = reference.get(subKey);
            var subValue = sub.get(subKey);
            var entryIsEqual = isSubMapEntryEqual(subValue, referenceValue);
            if (!entryIsEqual) {
                return false;
            }
        }
        return true;
    }

    private static boolean isSubMapEntryEqual(Object reference, Object actual) {
        if (reference instanceof Map m1 && actual instanceof Map m2) {
            return isSubMap(m1, m2);
        } else if (reference instanceof List referenceList && actual instanceof List actualList) {
            for (int i = 0; i < referenceList.size(); i += 1) {
                var referenceElement = referenceList.get(i);
                var actualElement = actualList.get(i);
                var isEqual = isSubMapEntryEqual(referenceElement, actualElement);
                if (!isEqual) {
                    return false;
                }
            }
        }
        return Objects.equals(reference, actual);
    }

    private static Map<String, Object> constructRandomStruct(
            Map<String, FieldDeclaration> referenceStruct, MockRandom random) {

        var sortedReferenceStruct = new ArrayList<>(referenceStruct.entrySet());
        Collections.sort(sortedReferenceStruct, (e1, e2) -> e1.getKey().compareTo(e2.getKey()));

        var obj = new TreeMap<String, Object>();
        for (var field : sortedReferenceStruct) {
            var fieldDeclaration = field.getValue();
            if (fieldDeclaration.optional && random.nextBoolean()) {
                continue;
            }
            obj.put(field.getKey(), constructRandomType(fieldDeclaration.typeDeclaration, random));
        }
        return obj;
    }

    private static Object constructRandomType(TypeDeclaration typeDeclaration, MockRandom random) {
        if (typeDeclaration.nullable && random.nextBoolean()) {
            return null;
        } else if (typeDeclaration.type instanceof JsonBoolean b) {
            return random.nextBoolean();
        } else if (typeDeclaration.type instanceof JsonInteger i) {
            return random.nextInt();
        } else if (typeDeclaration.type instanceof JsonNumber n) {
            return random.nextDouble();
        } else if (typeDeclaration.type instanceof JsonString s) {
            return random.nextString();
        } else if (typeDeclaration.type instanceof JsonArray a) {
            var length = random.nextInt(3);
            var array = new ArrayList<Object>();
            for (int i = 0; i < length; i += 1) {
                array.add(constructRandomType(a.nestedType, random));
            }
            return array;
        } else if (typeDeclaration.type instanceof JsonObject o) {
            var length = random.nextInt(3);
            var obj = new TreeMap<String, Object>();
            for (int i = 0; i < length; i += 1) {
                var key = random.nextString();
                obj.put(key, constructRandomType(o.nestedType, random));
            }
            return obj;
        } else if (typeDeclaration.type instanceof JsonAny a) {
            var selectType = random.nextInt(3);
            if (selectType == 0) {
                return random.nextBoolean();
            } else if (selectType == 1) {
                return random.nextInt();
            } else {
                return random.nextString();
            }
        } else if (typeDeclaration.type instanceof Struct s) {
            return constructRandomStruct(s.fields, random);
        } else if (typeDeclaration.type instanceof Enum e) {
            return constructRandomEnum(e.values, random);
        } else if (typeDeclaration.type instanceof Fn f) {
            return constructRandomStruct(f.arg.fields, random);
        }

        return null;
    }

    private static Map<String, Object> constructRandomEnum(Map<String, Struct> enumValuesReference,
            MockRandom random) {
        var sortedEnumValuesReference = new ArrayList<>(enumValuesReference.entrySet());
        Collections.sort(sortedEnumValuesReference, (e1, e2) -> e1.getKey().compareTo(e2.getKey()));

        var randomIndex = random.nextInt(sortedEnumValuesReference.size());
        var enumEntry = sortedEnumValuesReference.get(randomIndex);

        var enumValue = enumEntry.getKey();
        var enumData = enumEntry.getValue();

        return Map.of(enumValue, constructRandomStruct(enumData.fields, random));
    }

    static Map<String, Object> verify(String functionName, Map<String, Object> argument,
            boolean exactMatch,
            VerificationTimes verificationTimes, List<Invocation> invocations) {
        try {
            var matchesFound = 0;
            for (var invocation : invocations) {
                if (Objects.equals(invocation.functionName, functionName)) {
                    if (exactMatch) {
                        if (Objects.equals(invocation.functionArgument, argument)) {
                            invocation.verified = true;
                            matchesFound += 1;
                        }
                    } else {
                        if (InternalMockServer.isSubMap(argument, invocation.functionArgument)) {
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
                    verificationFailurePseudoJson = Map.of("tooManyMatchingCalls",
                            new TreeMap<>(Map.ofEntries(
                                    Map.entry("wanted", Map.of("exact", Map.of("times", e.times))),
                                    Map.entry("found", matchesFound),
                                    Map.entry("allCalls", allCallsPseudoJson))));
                } else if (matchesFound < e.times) {
                    verificationFailurePseudoJson = Map.of("tooFewMatchingCalls",
                            new TreeMap<>(Map.ofEntries(
                                    Map.entry("wanted", Map.of("exact", Map.of("times", e.times))),
                                    Map.entry("found", matchesFound),
                                    Map.entry("allCalls", allCallsPseudoJson))));
                }
            } else if (verificationTimes instanceof AtMostNumberOfTimes a) {
                if (matchesFound > a.times) {
                    verificationFailurePseudoJson = Map.of("tooManyMatchingCalls",
                            new TreeMap<>(Map.ofEntries(
                                    Map.entry("wanted", Map.of("atMost", Map.of("times", a.times))),
                                    Map.entry("found", matchesFound),
                                    Map.entry("allCalls", allCallsPseudoJson))));
                }
            } else if (verificationTimes instanceof AtLeastNumberOfTimes a) {
                if (matchesFound < a.times) {
                    verificationFailurePseudoJson = Map.of("tooFewMatchingCalls",
                            new TreeMap<>(Map.ofEntries(
                                    Map.entry("wanted", Map.of("atLeast", Map.of("times", a.times))),
                                    Map.entry("found", matchesFound),
                                    Map.entry("allCalls", allCallsPseudoJson))));

                }
            } else {
                throw new JApiProcessError("Unexpected verification times");
            }

            if (verificationFailurePseudoJson == null) {
                return Map.of("ok", Map.of());
            }

            return Map.of("errorVerificationFailure", Map.of("reason", verificationFailurePseudoJson));
        } catch (Exception ex) {
            throw new JApiProcessError(ex);
        }
    }

    static Map<String, Object> verifyNoMoreInteractions(List<Invocation> invocations) {
        try {
            var objectMapper = new ObjectMapper();
            var invocationsNotVerified = invocations.stream().filter(i -> !i.verified).toList();

            if (invocationsNotVerified.size() > 0) {
                var unverifiedCallsPseudoJson = new ArrayList<Map<String, Object>>();
                for (var invocation : invocationsNotVerified) {
                    var invocationArgumentPseudoJson = objectMapper.writeValueAsString(invocation.functionArgument);
                    unverifiedCallsPseudoJson.add(Map.of(invocation.functionName, invocationArgumentPseudoJson));
                }
                return Map.of("errorVerificationFailure",
                        Map.of("additionalUnverifiedCalls", unverifiedCallsPseudoJson));
            }

            return Map.of("ok", Map.of());
        } catch (Exception ex) {
            throw new JApiProcessError(ex);
        }
    }
}
